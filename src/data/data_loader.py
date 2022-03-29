import pandas as pd
from tqdm import tqdm
from weaviate import Client
from weaviate.util import generate_uuid5

from src import config
from src.models.weaviate.schema_1 import schema


class WeaviateDateLoader:
    def __init__(self, client: Client, batch_size: int = 30, dynamic: bool = True) -> None:
        self.client = client
        self.batch_size = batch_size
        self.dynamic = dynamic

        client.batch.configure(
            batch_size=30,
            dynamic=True,
        )

        self.schema = self._get_schema()
        self.reference_classes = self._get_reference_matches()

    def __enter__(self) -> "WeaviateDateLoader":
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> bool:
        self.client.batch.flush()
        # The __exit__() method returns a boolean value, either True or False.
        # If the return value is True, Python will make any exception silent.
        # Otherwise it doesn’t silence the exception.
        return False

    def _get_reference_matches(self) -> set[str]:

        reference_classes = set()
        for _class in self.client.schema.get()["classes"]:
            class_name = _class["class"]
            reference_class = f"has{class_name.title()}s"
            reference_classes.add(reference_class)

        return reference_classes

    def _get_schema(self) -> dict:
        schema = {}
        for _class in self.client.schema.get()["classes"]:
            properties: list[str] = []
            for class_property in _class["properties"]:
                properties.append(class_property["name"])

            schema[_class["class"]] = properties

        return schema

    def load(self, data: pd.DataFrame) -> None:

        class_uuid = {}
        reference_directions: list[tuple[str, str]] = []

        for _class in self.client.schema.get()["classes"]:

            class_name = _class["class"]
            weaviate_object = {}

            for _property in _class["properties"]:
                property_name = _property["name"]

                if property_name in self.reference_classes:
                    from_class = class_name
                    to_class = _property["dataType"][0]
                    reference_directions.append((from_class, to_class))
                else:
                    data_property_name = f"{class_name.lower()}_{property_name}"
                    weaviate_object[property_name] = data[data_property_name]

            uuid = generate_uuid5(class_name, weaviate_object)
            class_uuid[class_name] = uuid
            self.client.batch.add_data_object(
                uuid=uuid,
                data_object=weaviate_object,
                class_name=class_name,
            )

        for from_class, to_class in reference_directions:

            self.client.batch.add_reference(
                from_object_uuid=class_uuid[from_class],
                from_object_class_name=from_class,
                from_property_name=f"has{to_class.title()}s",
                to_object_uuid=class_uuid[to_class],
            )

    # def load(self, data: pd.DataFrame) -> None:

    #     reference_directions: list[tuple[str, str]] = list
    #     for class_name, properties in self.schema.items():
    #         weaviate_object = {}
    #         for property_name in properties:

    #             if property_name in self.reference_classes:
    #                 from_class = class_name

    #             property_name = f"{class_name.lower()}_{property_name}"
    #             weaviate_object[property_name] = data[property_name]

    #         self.client.batch.add_data_object(
    #             data_object=weaviate_object,
    #             class_name=class_name,
    #         )


def main() -> None:
    client = Client(f"{config.weaviate.host}:{config.weaviate.port}")
    client.schema.delete_all()
    client.schema.create(schema)
    # loader = WeaviateDateLoader(client)

    data = pd.read_csv(config.data.interim)
    data = data[:10]

    data["keywords"] = data["keywords"].apply(lambda x: [w.strip() for w in x.split(",")])
    data["descriptionWordCount"] = data["description"].str.count(" ") + 1
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
    data["award_name"] = data["author_name"].apply(lambda x: f"{x} award")
    data["publication_name"] = data["article_title"].apply(lambda x: f"Publication {x}")

    with WeaviateDateLoader(client) as loader:
        for _, row in tqdm(data.iterrows(), total=len(data)):
            loader.load(row)

    # client.batch.flush()


if __name__ == "__main__":

    main()
