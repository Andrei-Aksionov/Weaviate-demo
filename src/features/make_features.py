import random
from pathlib import Path

from tqdm import tqdm


def get_post_filenames(path: Path, limit: int = 1_000) -> list[Path]:

    # TODO: Tasks pending completion -@andreiaksionov at 1/28/2022, 5:37:15 PM
    # why to read all, shuffle and take only some portion when it can
    # be done all during obtaining file paths
    # TODO: Tasks pending completion -@andreiaksionov at 1/28/2022, 5:38:31 PM
    # check arguments types, especially returning type
    path = path.glob("**/*")
    file_paths = [x for x in path if x.is_file()]
    random.shuffle(file_paths)
    limit = min(len(file_paths), limit)

    return file_paths[:limit]


def read_posts(file_paths: list[Path]) -> list[str]:

    texts: list[str] = []

    for file_path in tqdm(file_paths):
        text = file_path.read_text(encoding="utf-8")

        # two new lines separate headers from body
        # we need to take only body without header

        start_body = text.find("/n/n")
        if start_body != -1:
            text = text[start_body:]

        # TODO: Tasks pending completion -@andreiaksionov at 1/28/2022, 5:49:55 PM
        # make it a separate function
        # if text contains less then 10 words -> skip it
        if len(text.split()) < 10:
            continue

        text = text.replace("\n", " ").replace("\t", " ").strip()

        if len(text) > 1_000:
            text = text[:1_000]

        texts.append(text)

    return texts


if __name__ == "__main__":
    files = get_post_filenames(Path("data/raw"), limit=10)
    posts = read_posts(files)
    print(posts)
