import json
import pickle

import weaviate
from tqdm import tqdm, trange
from weaviate.batch import Batch
from weaviate.util import generate_uuid5


def add_article(batch: Batch, article_data: dict) -> str:

    article_object = {
        "title": article_data["title"],
        "summary": article_data["summary"].replace("\n", " "),
    }
    article_id = article_data["id"]
    # title_vector = article_data["title_vector"]

    # adding article to the batch
    batch.add_data_object(
        data_object=article_object,
        class_name="Article",
        uuid=article_id,
        # vector=title_vector,
    )

    return article_id


def add_author(batch: Batch, author_name: str, created_authors: dict) -> str:

    if author_name in created_authors:
        # return author uuid
        return created_authors[author_name]

    # generate UUID for the author
    author_id = generate_uuid5(author_name)
    author_object = {
        "name": author_name,
    }

    # add author to the batch
    batch.add_data_object(
        data_object=author_object,
        class_name="Author",
        uuid=author_id,
    )

    created_authors[author_name] = author_id

    return author_id


def add_references(batch: Batch, article_id: str, author_id: str) -> None:

    # add references to the batch

    # author -> article
    batch.add_reference(
        from_object_uuid=author_id,
        from_object_class_name="Author",
        from_property_name="wroteArticles",
        to_object_uuid=article_id,
    )

    # article -> author
    batch.add_reference(
        from_object_uuid=article_id,
        from_object_class_name="Article",
        from_property_name="hasAuthors",
        to_object_uuid=author_id,
    )


def load_data(client: weaviate.Client):

    created_authors = {}

    with open("data/raw/newspaper_news.pkl", "rb") as fin:
        data = pickle.load(fin)

    # with open("data/interim/news_title_vectors.pkl", "rb") as fin:
    #     data = pickle.load(fin)

    with client.batch as batch:
        for data_object in tqdm(data, disable=False):

            article_id = add_article(batch, data_object)

            for author in data_object["authors"]:
                author_id = add_author(batch, author, created_authors)

                add_references(batch, article_id, author_id)


# def load_data_manual(client: weaviate.Client) -> None:

#     created_authors = {}

#     with open("data/raw/newspaper_news.pkl", "rb") as fin:
#         data = pickle.load(fin)

#     with client.batch as batch:
#         for idx, data_object in enumerate(tqdm(data)):

#             article_id = add_article(batch, data_object)

#             for author in data_object["authors"]:
#                 author_id = add_author(batch, author, created_authors)

#                 add_references(batch, article_id, author_id)

#         if idx % 20 == 0:
#             batch.create_objects()
#             batch.create_references()


def load_schema(client: weaviate.Client) -> None:
    with open("src/models/weaviate/schema_vectorizer.json", "r") as fin:
        schema = json.load(fin)

    client.schema.delete_all()
    client.schema.create(schema)

    # from src.models.weaviate.schemas import combined_class_schema

    # client.schema.delete_all()
    # client.schema.create(combined_class_schema)


def erase(client: weaviate.Client) -> None:
    for object in client.data_object.get()["objects"]:
        id_to_delete = object["id"]
        client.data_object.delete(id_to_delete)

    client.schema.delete_all()


def main():
    client = weaviate.Client("http://localhost:8080")
    client.batch.configure(
        batch_size=30,
        dynamic=True,
    )

    # erase(client)

    load_schema(client)
    load_data(client)
    articles_count = client.query.aggregate(class_name="Article").with_meta_count().do()
    authors_count = client.query.aggregate(class_name="Author").with_meta_count().do()
    print(f"Articles: {articles_count}, Authors: {authors_count}")


if __name__ == "__main__":
    main()
