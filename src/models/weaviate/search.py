from time import time

import sentence_transformers
import weaviate

from src.features.vectorization import text_to_vec


def search(query, client, tokenizer, model, limit=3):
    before = time()
    vec = text_to_vec(query, tokenizer, model)
    vec_took = time() - before

    before = time()
    near_vec = {"vector": vec.tolist()}
    res = (
        client.query.get("Post", ["content", "_additional {certainty}"])
        .with_near_vector(near_vec)
        .with_limit(limit)
        .do()
    )
    search_took = time() - before

    print(
        '\nQuery "{}" with {} results took {:.3f}s ({:.3f}s to vectorize and {:.3f}s to search)'.format(
            query, limit, vec_took + search_took, vec_took, search_took
        )
    )
    for post in res["data"]["Get"]["Post"]:
        print("{:.4f}: {}".format(post["_additional"]["certainty"], post["content"]))
        print("---")


def search_sbert(
    query: str, client: weaviate.Client, model: sentence_transformers.SentenceTransformer, limit: int = 1
) -> str:

    near_vector = {"vector": model.encode(query)}
    response = (
        client.query.get("Article", ["title", "_additional {certainty}"])
        .with_near_vector(near_vector)
        .with_limit(limit)
        .do()
    )

    response_repr = ""
    for post in response["data"]["Get"]["Article"]:
        response_repr += "{:.4f}: {}".format(post["_additional"]["certainty"], post["title"])
        response_repr += "\n---\n"

    return response_repr
