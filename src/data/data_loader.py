from collections import defaultdict
from typing import Dict

from weaviate import Client
from weaviate.util import generate_uuid5

from src.utils.helper_utils import ravel


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
        # to prevent from sending the same object multiple times will store ids
        # Weaviate will not create duplicates but the problem is that sending
        # the same object multiple times will slow down the procedure
        self.created_classes_id = defaultdict(set)

    def __enter__(self) -> "WeaviateDateLoader":
        return self

    def __exit__(self, *_) -> bool:
        self.client.batch.flush()
        # The __exit__() method returns a boolean value, either True or False.
        # If the return value is True, Python will make any exception silent.
        # Otherwise it doesn’t silence the exception.
        return False

    def __parse_schema(self) -> dict:
        # TODO: put docstring

        schema = self.client.schema.get()
        parsed_schema = defaultdict(lambda: defaultdict(list))

        # expected references like hasAuthors, hasArticles
        expected_references = {f"has{c['class'].title()}s" for c in schema["classes"]}

        for _class in schema["classes"]:
            class_name = _class["class"]

            for _property in _class["properties"]:
                if _property["name"] in expected_references:
                    parsed_schema[class_name]["referenced_to"].append(
                        {
                            "name": _property["name"],
                            "dataType": ravel(_property["dataType"]),
                        }
                    )
                else:
                    property_name = _property["name"]
                    # by convention data has keys as [class_name]_[property_name]
                    # e.g. article_title
                    data_accessor = f"{class_name.lower()}_{property_name}"
                    parsed_schema[class_name]["properties"].append(
                        {
                            "name": property_name,
                            "data_accessor": data_accessor,
                        }
                    )

        return parsed_schema

    def load(self, data: dict) -> None:
        # TODO: docstring

        created_objects_id = {}

        for class_name in self.schema:

            properties = self.schema[class_name]["properties"]

            # what will be send to weaviate
            # key of that dictionary has to be identical to class property name
            # without any class_name prefix
            weaviate_object = {p["name"]: data[p["data_accessor"]] for p in properties}

            id = generate_uuid5((class_name, weaviate_object))
            created_objects_id[class_name] = id

            # if such an object was already added - skip
            # e.g. multiple article might have the same author
            # that means that we don't need to send the same author
            # multiple times to weaviate
            if id not in self.created_classes_id[class_name]:
                self.created_classes_id[class_name].add(id)

                self.client.batch.add_data_object(
                    uuid=id,
                    data_object=weaviate_object,
                    class_name=class_name,
                )

        # adds linkage between referenced objects
        # e.g. Article should reference on Author and Author should reference
        # to all written Articles
        self.__add_reference(created_objects_id)

    def __add_reference(self, created_objects_id: Dict[str, str]) -> None:
        # TODO: small docstring

        for from_what_class in self.schema:

            from_what_object_id = created_objects_id[from_what_class]

            for reference in self.schema[from_what_class]["referenced_to"]:

                linked_by_what_property = reference["name"]
                to_what_class = reference["dataType"]
                to_what_object_id = created_objects_id[to_what_class]

                self.client.batch.add_reference(
                    from_object_uuid=from_what_object_id,
                    from_object_class_name=from_what_class,
                    from_property_name=linked_by_what_property,
                    to_object_uuid=to_what_object_id,
                )
