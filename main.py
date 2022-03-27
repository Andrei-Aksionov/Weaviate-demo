"""
Example script with search against vectorized articles using Weaviate.

The script will run a single query and print output.
More examples of available queries can be found in notebooks/2.data_preprocessing.ipynb notebook.
"""

import weaviate

from src.utils.search import pprint_response


def main():

    # instantiate connection to a running weaviate instance
    # to start weaviate use src/docker/weaviate/docker-compose.yaml
    client = weaviate.Client("http://localhost:8080")

    ### construct query request ###
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

    # running query
    response = (
        client.query.get(class_name, properties).with_near_text(nearText).with_where(where_filter).with_limit(5).do()
    )

    pprint_response(response)


if __name__ == "__main__":
    main()
