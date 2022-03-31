# TODO: Tasks pending completion -@andreiaksionov at 3/28/2022, 5:25:12 PM
# put this as a pseudo-code in .md description

import pandas as pd
import weaviate
from tqdm import tqdm
from weaviate.batch import Batch
from weaviate.util import generate_uuid5

from src.models.weaviate import schema
from src.utils.config import config
from src.utils.weaviate_stats import print_article_stats


def split_string(text: str, delimeter: str = ",") -> list[str]:
    return [w.strip() for w in text.split(delimeter)]


def add_author(batch: Batch, author_name: str) -> str:

    # generate UUID for the author
    author_id = generate_uuid5(author_name)
    author_object = {"name": author_name}

    # add author to the batch
    batch.add_data_object(
        data_object=author_object,
        class_name="Author",
        uuid=author_id,
    )

    return author_id


def add_article(batch: Batch, article_data: pd.Series) -> str:

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


def load_data(client: weaviate.Client, data: pd.DataFrame) -> None:

    authors_dict = {}

    with client.batch as batch:

        for data_object in tqdm(data.itertuples(), total=len(data)):

            article_id = add_article(batch, data_object)

            authors = split_string(data_object.author)
            for author in authors:

                # as number authors is smaller that number of articles (EDA paragraph 2.4)
                # there is no need to add author to batch if it is already added
                # that will speed up loading process
                if author not in authors_dict:
                    author_id = generate_uuid5(author)
                    authors_dict[author] = author_id
                else:
                    author_id = add_author(batch, author)
                add_references(batch, article_id, author_id)


def load_schema(client: weaviate.Client) -> None:

    client.schema.delete_all()
    client.schema.create(schema.schema)


def main() -> None:
    # instantiate connection with Weaviate
    client = weaviate.Client("http://localhost:8080")
    # configure the size of batch
    # more about different version of batch is written in article
    # https://towardsdatascience.com/getting-started-with-weaviate-python-client-e85d14f19e4f
    # and in docs
    # https://weaviate-python-client.readthedocs.io/en/latest/weaviate.batch.html
    client.batch.configure(
        batch_size=30,
        dynamic=True,
    )

    # reading data that will be pushed to Weaviate
    data = pd.read_csv(config.data.path.interim)
    # data = data.iloc[:50]

    # schema describes the structure of the data
    # good article with examples:
    # https://hackernoon.com/what-is-weaviate-and-how-to-create-data-schemas-in-it-7hy3460
    load_schema(client)

    # load data
    load_data(client, data)

    # show number of objects per each class
    print_article_stats(client)


if __name__ == "__main__":
    main()
