"""
# TODO: finalize

This script does two things:
1. Populates weaviate instance with data
2. Runs search query against indexed and vectorized data
"""

import json

import pandas as pd
from tqdm import tqdm
from weaviate import Client

from src import config
from src.data.data_loader import WeaviateDateLoader
from src.utils.helper_utils import add_schema, split_string
from src.utils.weaviate_utils import pprint_response, print_article_stats


def load_data(client: Client, data: pd.DataFrame) -> None:

    with WeaviateDateLoader(client) as loader:

        for _, row in tqdm(data.iterrows(), total=len(data), ascii=True):

            # some articles have multiple authors
            # in order to create `Author` weaviate object for each author
            # we need to unfold articles
            # for example:
            #                                                |--------------------------|
            # --------------------------------------         | "article_1" | "author_1" |
            # | "article_1" | "author_1, author_2" |   -->   ----------------------------
            # --------------------------------------         | "article_1" | "author_2" |
            #                                                ----------------------------
            # Weaviate data loader will not sent
            # the same object to weaviate more than once

            row["author_name"] = split_string(row["author_name"])
            row = row.to_frame().T.explode("author_name")

            for _, inner_row in row.iterrows():
                inner_row = dict(inner_row)

                inner_row["article_keywords"] = split_string(inner_row["article_keywords"])
                inner_row["article_descriptionWordCount"] = inner_row["article_description"].count(" ") + 1

                loader.load(inner_row)


def search(client: Client) -> dict:

    # --- construct query request --- #
    # concepts for vector search
    nearText = {
        "concepts": ["banks hedge fonds predictions"],
        "certainty": 0.5,
    }

    # against what class run query
    class_name = "Article"
    # what fields to return
    properties = [
        "title",
        "keywords",
        "short_description",
        "_additional {certainty}",
    ]
    # filter candidates by keywords
    where_filter = {
        "operator": "Equal",
        "path": ["keywords"],
        "valueText": ["bonds"],
    }

    # --- running query --- #
    response = (
        client.query.get(class_name=class_name, properties=properties)
        .with_near_text(content=nearText)
        .with_where(content=where_filter)
        .with_limit(limit=5)
        .do()
    )

    return response


def main() -> None:
    client = Client(f"{config.weaviate.host}:{config.weaviate.port}")

    with open(config.data.path.schema) as fin:
        schema = json.load(fin)
    add_schema(client, schema)

    # --------- LOAD DATA ---------  #
    data = pd.read_csv(config.data.path.interim)
    # NOTE: Needs discussion or investigation -@andreiaksionov at 3/31/2022, 3:25:58 PM
    # only for debug purpose
    data = data[:50]

    # as different classes might have the same name in order to access data correctly
    # we need to rename columns to a format that is expected by data loader:
    # [class_name]_[property_name] -> article_title, author_name, ..
    data = data.rename(columns=config.data.loader.names_map)

    load_data(client, data)
    # show number of objects per each class
    print_article_stats(client)

    # --------- SEARCH ---------  #
    response = search(client)
    pprint_response(response)


if __name__ == "__main__":
    main()
