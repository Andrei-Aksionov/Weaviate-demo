from typing import Optional

from termcolor import colored
from weaviate import Client


def pprint_response(response: dict) -> None:
    """Prints response in a prettier way.

    Parameters
    ----------
    response : dict
    """
    response = response["data"]["Get"]

    for class_name in response:
        print(colored(class_name.upper(), "red", "on_white", attrs=["bold"]))

        # if nothing was found for this class
        if not response[class_name]:
            print(colored("Empty result", "red", "on_grey"))
            continue

        for idx, resp in enumerate(response[class_name]):
            print(f"Response # {idx}")
            for key, value in resp.items():
                print(f"{colored(key, 'magenta', 'on_grey')}: {value}")
            print("=" * 120)


def print_weaviate_class_stats(client: Client, allowed_classes: Optional[list[str]] = None) -> None:
    """Prints info of how many object per each class there are in Weaviate instance.

    Parameters
    ----------
    client : Client
        connection to Weaviate instance
    allowed_classes : Optional[list[str]], optional
        if provided only this classes info will be displayed, by default None
    """
    for weaviate_class in client.schema.get()["classes"]:
        class_name = weaviate_class["class"]
        if allowed_classes and class_name not in allowed_classes:
            continue
        response = client.query.aggregate(class_name).with_meta_count().do()
        class_object_count = response["data"]["Aggregate"][class_name][0]["meta"]["count"]
        print(f"Class name: {class_name}\n\tObjects count: {class_object_count}")


def add_schema(client: Client, schema: dict, delete_all: bool = True) -> None:
    """Adds schema to Weaviate instance.

    Parameters
    ----------
    client : Client
        connection to Weaviate instance
    schema : dict
        schema file that describes classes, their properties with data types and references to other classes
    delete_all : bool, optional
        remove the entire schema from the Weaviate instance and all data associated with it, by default True
    """
    if delete_all:
        client.schema.delete_all()
    client.schema.create(schema)
