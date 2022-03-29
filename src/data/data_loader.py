from collections import defaultdict
from typing import Dict

import pandas as pd
from tqdm import tqdm
from weaviate import Client
from weaviate.util import generate_uuid5

from src import config
from src.models.weaviate.schema import schema
from src.utils.helper_utils import split_string


class WeaviateDateLoader:
    def __init__(self, client: Client, batch_size: int = 30, dynamic: bool = True) -> None:
        self.client = client
        self.batch_size = batch_size
        self.dynamic = dynamic

        client.batch.configure(
            batch_size=30,
            dynamic=True,
        )

        self.schema = self.__parse_schema()
        self.created_classes = defaultdict(set)

    def __enter__(self) -> "WeaviateDateLoader":
        return self

    def __exit__(self, *_) -> bool:
        self.client.batch.flush()
        # The __exit__() method returns a boolean value, either True or False.
        # If the return value is True, Python will make any exception silent.
        # Otherwise it doesn’t silence the exception.
        return False

    def __parse_schema(self) -> dict:

        schema = self.client.schema.get()
        parsed_schema = {}

        # expected references like hasAuthors, hasArticles
        expected_references = {f"has{c['class'].title()}s" for c in schema["classes"]}

        for _class in schema["classes"]:
            class_name = _class["class"]

            properties = []
            for _property in _class["properties"]:
                _property_name = _property["name"]
                if _property_name in expected_references:
                    # if it's a reference like hasAuthors, then also add
                    # info about dataType (e.g. Author)
                    properties.append(
                        {
                            "name": _property_name,
                            "dataType": _property["dataType"][0],
                        }
                    )
                else:
                    properties.append(_property_name)

            parsed_schema[class_name] = properties

        return parsed_schema

    def load(self, data: dict) -> None:

        class_id = {}
        object_relations = []

        for class_name, properties in self.schema.items():

            # what will be send to weaviate
            weaviate_object = {}

            for _property in properties:

                if isinstance(_property, str):
                    # keys in data object are encoded as
                    # [class_name]_[property_name]
                    # example: article_title
                    data_property_name = f"{class_name.lower()}_{_property}"
                    weaviate_object[_property] = data[data_property_name]
                else:
                    from_class = class_name
                    to_class = _property["dataType"]
                    object_relations.append((from_class, to_class))

            id = generate_uuid5((class_name, weaviate_object))
            class_id[class_name] = id

            if id not in self.created_classes[class_name]:
                self.created_classes[class_name] = id

                self.client.batch.add_data_object(
                    uuid=id,
                    data_object=weaviate_object,
                    class_name=class_name,
                )

        self.__add_references(object_relations, class_id)

    def __add_references(self, object_relations: list[tuple[str, str]], class_uuid: dict) -> None:

        for from_class, to_class in object_relations:

            self.client.batch.add_reference(
                from_object_uuid=class_uuid[from_class],
                from_object_class_name=from_class,
                from_property_name=f"has{to_class.title()}s",
                to_object_uuid=class_uuid[to_class],
            )


def main() -> None:
    client = Client(f"{config.weaviate.host}:{config.weaviate.port}")
    client.schema.delete_all()
    client.schema.create(schema)

    data = pd.read_csv(config.data.interim)
    data = data[:10]
    # data = data[6:8]

    # ---------------------
    # TODO: put it in config
    names_map = {
        "title": "article_title",
        "url": "article_url",
        "published_at": "article_published_at",
        "short_description": "article_short_description",
        "description": "article_description",
        "keywords": "article_keywords",
        "descriptionWordCount": "article_descriptionWordCount",
        "author": "author_name",
    }

    data = data.rename(columns=names_map)

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


if __name__ == "__main__":

    main()
