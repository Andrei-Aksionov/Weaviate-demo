import json
import pickle
import uuid

import newspaper
from tqdm import trange


def parse_article_from_newspapers(news_url: str, max_articles: int = 100) -> list[str]:
    articles: list[str] = []

    news_builder = newspaper.build(news_url, memoize_articles=False)

    max_articles = min(max_articles, news_builder.size())

    for idx in trange(max_articles):
        article = news_builder.articles[idx]

        try:
            article.download()
            article.parse()
            article.nlp()

            # if all(article.title, article.summary, article.authors):
            if article.title and article.summary and article.text and article.authors:
                article.id = str(uuid.uuid3(uuid.NAMESPACE_DNS, article.url))

                articles.append(
                    {
                        "id": article.id,
                        "title": article.title,
                        "summary": article.summary,
                        "authors": article.authors,
                    }
                )

        except:
            print("Issue while loading article. Skipping...")

    return articles


if __name__ == "__main__":
    articles = []
    limit = 100
    for url in ("https://edition.cnn.com", "https://www.theguardian.com/international"):
        articles.extend(parse_article_from_newspapers(url, limit))
    print(len(articles))

    with open("data/raw/newspaper_news.pkl", "wb") as fout:
        pickle.dump(articles, fout)
