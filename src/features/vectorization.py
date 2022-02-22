import os
import pickle
from pathlib import Path

import nltk
import torch
from nltk.tokenize import sent_tokenize
from tqdm import tqdm
from transformers import AutoModel, AutoTokenizer

from src.features.make_features import get_post_filenames, read_posts

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
torch.set_grad_enabled(False)


def text_to_vec(text: str, tokenizer, model):

    tokens_pt = tokenizer(
        text, padding=True, truncation=True, max_length=500, add_special_tokens=True, return_tensors="pt"
    )
    tokens_pt.to(DEVICE)
    outputs = model(**tokens_pt)
    outputs = outputs[0].mean(0).mean(0)

    return outputs.detach()


def vectorize_texts(texts: list[str], tokenizer, model):

    text_vectors: list[list[float]] = []

    for text in tqdm(texts):
        tokens = sent_tokenize(text)
        vector = text_to_vec(tokens, tokenizer, model)
        text_vectors.append(vector)

    return text_vectors


def main():
    # udpated to use different model if desired
    MODEL_NAME = "distilbert-base-uncased"
    # MODEL_NAME = "philschmid/MiniLM-L6-H384-uncased-sst2"
    model = AutoModel.from_pretrained(MODEL_NAME)
    model.to(DEVICE)  # remove if working without GPUs
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    # initialize nltk (for tokenizing sentences)
    nltk.download("punkt")

    files = get_post_filenames(Path("data/raw"), limit=1_000)
    posts = read_posts(files)
    with open("data/interim/posts.pkl", "wb") as fout:
        pickle.dump(posts, fout)
    vectors = vectorize_texts(posts, tokenizer, model)

    with open("models/vectors.pkl", "wb") as fout:
        pickle.dump(vectors, fout)

    with open("models/vectors.pkl", "rb") as fin:
        vectors_1 = pickle.load(fin)

    for v, v1 in zip(vectors, vectors_1):
        assert (v == v1).all()
    print("Hello")


if __name__ == "__main__":
    main()
