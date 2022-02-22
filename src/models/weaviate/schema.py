def init_weaviate_schema(client):
    # a simple schema containing just a single class for our posts
    schema = {
        "classes": [
            {
                "class": "Post",
                "vectorizer": "text2vec-transformers",  # explicitly tell Weaviate not to vectorize anything, we are providing the vectors ourselves through our BERT model
                "properties": [
                    {
                        "name": "content",
                        "dataType": ["text"],
                    }
                ],
            }
        ]
    }

    # cleanup from previous runs
    client.schema.delete_all()
    client.schema.create(schema)
    print("Schema initiated")
