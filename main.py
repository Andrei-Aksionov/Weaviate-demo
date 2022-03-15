import pickle

# import torch
import weaviate

# from src.features.vectorization import vectorize_texts
# from src.models.weaviate.data_import import import_posts, import_posts_with_vectors
# from src.models.weaviate.schema import init_weaviate_schema
# from src.models.weaviate.search import search, search_sbert

# from sentence_transformers import SentenceTransformer
# from transformers import AutoModel, AutoTokenizer


# DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
# torch.set_grad_enabled(False)
# from functools import partial


def prettify_response(response: dict, field: str) -> str:
    response_repr = ""
    for post in response["data"]["Get"]["Article"]:
        response_repr += "{:.4f}: {}".format(post["_additional"]["certainty"], post[field])
        response_repr += "\n---\n"

    return response_repr


def main():

    client = weaviate.Client("http://localhost:8080")
    # init_weaviate_schema(client)
    # with open("data/interim/posts.pkl", "rb") as fin:
    #     posts = pickle.load(fin)
    # with open("models/vectors.pkl", "rb") as fin:
    #     vectors = pickle.load(fin)

    # import_posts_with_vectors(posts, vectors, client)
    # import_posts(posts, client)
    # total_count = client.query.aggregate(class_name="post").with_meta_count().do()
    # print(f"Total count: {total_count}")
    articles_count = client.query.aggregate(class_name="Article").with_meta_count().do()
    authors_count = client.query.aggregate(class_name="Author").with_meta_count().do()
    print(f"Articles: {articles_count}, Authors: {authors_count}\n")

    # MODEL_NAME = "distilbert-base-uncased"
    # MODEL_NAME = "philschmid/MiniLM-L6-H384-uncased-sst2"
    # model = AutoModel.from_pretrained(MODEL_NAME)
    # model.to(DEVICE)  # remove if working without GPUs
    # tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    ### search
    # vector_search = partial(search, client=client, model=model, tokenizer=tokenizer)
    # print(search("the best camera lens", client, 1))
    # print(vector_search(query="the best camera lens", limit=1))
    # print(vector_search(query="motorcycle trip", limit=1))
    # print(vector_search(query="which software do i need to view jpeg files", limit=1))
    # print(vector_search(query="windows vs mac", limit=1))
    # print(vector_search("video driver", limit=1))

    ### search with transformers module

    # model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
    # query_text = "Nike"
    # query_vector = {"vector": model.encode(query_text)}
    # response = (
    #     client.query.get("Article", ["title", "_additional {certainty}"])
    #     .with_near_vector(query_vector)
    #     .with_limit(1)
    #     .do()
    # )
    nearText = {
        "concepts": ["financial crisis"],
        "certainty": 0.5,
        # "moveAwayFrom": {"concepts": ["britain"], "force": 0.8},
        # "moveTo": {"concepts": ["new york"], "force": 0.85},
    }
    field = "description title"
    response = (
        client.query.get("Article", [field, "_additional {certainty} "]).with_near_text(nearText).with_limit(5).do()
    )
    # # print(response)
    # for post in response["data"]["Get"]["Article"]:
    #     print("{:.4f}: {}".format(post["_additional"]["certainty"], post["title"]))
    #     print("---")

    # query_text = "sport"
    # response = search_sbert(query_text, client, model, 5)
    response = prettify_response(response, "title")
    print(response)


if __name__ == "__main__":
    main()
