"""
This script does two things:
1. Populates weaviate instance with data
2. Runs search query against indexed and vectorized data
"""

import json

import pandas as pd
from tqdm import tqdm
from weaviate import Client

from src import config
from src.data import WeaviateDateLoader
from src.utils import (
    add_schema,
    pprint_response,
    print_weaviate_class_stats,
    split_string,
)


def load_data(client: Client, data: pd.DataFrame) -> None:
    """Loads data into Weaviate instance.

    Parameters
    ----------
    client : Client
        connection to Weaviate instance
    data : pd.DataFrame
        data that will be loaded into Weaviate instance
    """
    with WeaviateDateLoader(client) as loader:

        for _, row in tqdm(data.iterrows(), total=len(data), ascii=True):

            # some articles have multiple authors
            # in order to create `Author` object for each author
            # we need to unfold articles
            # for example:
            #                                                ----------------------------
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
    """Search example.

    Parameters
    ----------
    client : Client
        connection to Weaviate instance

    Returns
    -------
    dict
        dictionary with response
    """
    # ----------- CONSTRUCT QUERY REQUEST ----------- #
    # concepts for vector search
    nearText = {
        "concepts": ["banks hedge fonds predictions"],
        "certainty": 0.5,
    }
    # against what class to run query
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

    # ---------------- RUN QUERY ---------------- #
    response = (  # noqa: says that expression is too complex
        client.query.get(class_name=class_name, properties=properties)
        .with_near_text(content=nearText)
        .with_where(content=where_filter)
        .with_limit(limit=5)
        .do()
    )

    return response


def main() -> None:
    """Main function.

    Creates connection to Weaviate instance, creates schema inside it, loads data,
    outputs information with number of objects per each class
    and runs example search query as a sanity check.
    """
    # --------- CREATE CONNECTION ---------  #
    client = Client(f"{config.weaviate.instance.host}:{config.weaviate.instance.port}")

    # ----------- CREATE SCHEMA -----------  #
    with open(config.weaviate.schema.path) as fin:
        schema = json.load(fin)
    add_schema(client, schema)

    # ------------- LOAD DATA -------------  #
    data = pd.read_csv(config.data.path.interim)
    # as different classes might have the same name, in order to access data correctly
    # we need to rename columns to a format that is expected by data loader:
    # [class_name]_[property_name] -> article_title, author_name, ..
    data = data.rename(columns=config.data.loader.names_map)
    load_data(client, data)

    # --------- PRINT CLASS STATS ----------  #
    # show number of objects per each class
    print_weaviate_class_stats(client)

    # ------------- DO SEARCH --------------  #
    response = search(client)
    pprint_response(response)


if __name__ == "__main__":
    main()
