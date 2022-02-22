import weaviate
from tqdm import tqdm


def import_posts_with_vectors(posts, vectors, client: weaviate.Client):
    if len(posts) != len(vectors):
        raise Exception("len of posts ({}) and vectors ({}) does not match".format(len(posts), len(vectors)))

    for post, vector in zip(tqdm(posts), vectors):
        client.data_object.create(
            data_object={"content": post},
            class_name="Post",
            vector=vector,
        )


def import_posts(posts, client: weaviate.Client):
    for post in tqdm(posts):
        client.data_object.create(
            data_object={"content": post},
            class_name="Post",
        )
