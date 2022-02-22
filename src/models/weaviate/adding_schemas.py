import json

import weaviate

from src.models.weaviate.schemas import (
    article_class_schema,
    author_class_schema,
    combined_class_schema,
)


def prettify(schema: dict) -> str:
    return json.dumps(schema, indent=2)


def main():
    client = weaviate.Client("http://localhost:8080")
    # total_count = client.query.aggregate(class_name="post").with_meta_count().do()
    # print(f"Total count: {total_count}")
    client.schema.delete_all()
    # client.schema.create(article_class_schema)
    # client.schema.create(author_class_schema)
    client.schema.create(combined_class_schema)
    # print(prettify(client.schema.get()))

    with open("src/models/weaviate/schema_dumped.json", "w") as fout:
        json.dump(client.schema.get(), fout, indent=2)

    # with open("src/models/weaviate/schema_dumped.json", "r") as fin:
    #     schema = json.load(fin)

    # client.schema.create(schema)

    # print(prettify(client.schema.get()))


if __name__ == "__main__":
    main()
