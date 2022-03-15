import pandas as pd
import weaviate
from tqdm import tqdm, trange
from weaviate.batch import Batch
from weaviate.util import generate_uuid5

from src.models.weaviate import schema
from src.utils.config import config


def split_string(text: str, delimeter: str = ",") -> list[str]:
    return [kw.strip() for kw in text.split(delimeter)]


class DataLoader:
    def __init__(self) -> None:
        self.authors: dict[str, str] = {}

    def add_author(self, batch: Batch, author_name: str) -> str:

        if author_id := self.authors.get(author_name):
            return author_id

        # generate UUID for the author
        author_id = generate_uuid5(author_name)
        author_object = {"name": author_name}

        # add author to the batch
        batch.add_data_object(
            data_object=author_object,
            class_name="Author",
            uuid=author_id,
        )

        self.authors[author_name] = author_id

        return author_id

    def add_article(self, batch: Batch, article_data: pd.Series) -> str:

        keywords = split_string(article_data.keywords)

        description_word_count = article_data.description.count(" ") + 1
        article_object = {
            "title": article_data.title,
            "url": article_data.url,
            "published_at": article_data.published_at,
            "short_description": article_data.short_description,
            "description": article_data.description,
            "keywords": keywords,
            "descriptionWordCount": description_word_count,
        }

        article_id = generate_uuid5(article_data.url)
        # adding article to the batch
        batch.add_data_object(
            data_object=article_object,
            class_name="Article",
            uuid=article_id,
        )

        return article_id

    def add_references(self, batch: Batch, article_id: str, author_id: str) -> None:

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


def load_data(client: weaviate.Client, data: pd.DataFrame) -> None:

    data_loader = DataLoader()

    with client.batch as batch:
        for data_object in tqdm(data.itertuples(), total=len(data)):

            article_id = data_loader.add_article(batch, data_object)

            authors = split_string(data_object.author)
            for author in authors:
                author_id = data_loader.add_author(batch, author)

                data_loader.add_references(batch, article_id, author_id)


def load_schema(client: weaviate.Client) -> None:

    client.schema.delete_all()
    client.schema.create(schema.schema)


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

    data = pd.read_csv(config.data.interim)

    load_schema(client)
    load_data(client, data)
    articles_count = client.query.aggregate(class_name="Article").with_meta_count().do()
    authors_count = client.query.aggregate(class_name="Author").with_meta_count().do()
    print(f"Articles: {articles_count}, Authors: {authors_count}")


if __name__ == "__main__":
    main()
