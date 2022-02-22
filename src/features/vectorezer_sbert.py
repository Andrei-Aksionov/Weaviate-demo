import pickle

import numpy as np
import tqdm
from sentence_transformers import SentenceTransformer


def vectorize_text(text: str, model) -> np.array:
    return model.encode(text)


def test():
    # Our sentences we like to encode
    sentences = [
        "This framework generates embeddings for each input sentence",
        "Sentences are passed as a list of string.",
        "The quick brown fox jumps over the lazy dog.",
    ]

    model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
    embeddings = vectorize_text(sentences, model)
    # Print the embeddings
    for sentence, embedding in zip(sentences, embeddings):
        print("Sentence:", sentence)
        print("Embedding:", embedding)
        print("")


def main():
    with open("data/raw/newspaper_news.pkl", "rb") as fin:
        data = pickle.load(fin)

    model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

    for idx in tqdm.trange(len(data)):
        title = data[idx]["title"]
        vector = model.encode(title)
        data[idx]["title_vector"] = vector

    with open("data/interim/news_title_vectors.pkl", "wb") as fout:
        pickle.dump(data, fout)


if __name__ == "__main__":
    main()
