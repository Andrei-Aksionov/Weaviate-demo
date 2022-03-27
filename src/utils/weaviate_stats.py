from typing import Optional

from weaviate import Client


def print_article_stats(client: Client, allowed_classes: Optional[list[str]] = None) -> None:
    for weaviate_class in client.schema.get()["classes"]:
        class_name = weaviate_class["class"]
        if allowed_classes and class_name not in allowed_classes:
            continue
        response = client.query.aggregate(class_name).with_meta_count().do()
        class_object_count = response["data"]["Aggregate"][class_name][0]["meta"]["count"]
        print(f"Class name: {class_name}\n\tObjects count: {class_object_count}")
