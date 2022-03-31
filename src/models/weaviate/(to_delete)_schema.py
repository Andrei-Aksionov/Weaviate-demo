# TODO: Tasks pending completion -@andreiaksionov at 3/28/2022, 2:52:40 PM
# Decide either to use .py (with comments) or .json file (without comments)
# fmt: off
# flake8: noqa
schema = {
  "classes": [
    {
      "class": "Article",
      "description": "An Article class to store the article summary and it's authors",
      "vectorizer": "text2vec-transformers",
      "properties": [
        {
          "name": "title",
          "dataType": ["text"],
          "description": "The title of the article"
        },
        {
          "name": "url",
          "dataType": ["string"],
          "description": "Url of the article",
          "moduleConfig": {
            "text2vec-transformers": {
              "skip": True, # if true, the whole property will NOT be included in vectorization. default is false, meaning that the object will be NOT be skipped
            },
          },
        },
        {
          "name": "published_at",
          "dataType": ["date"],
          "description": "Date of publication"
        },
        {
          "name": "short_description",
          "dataType": ["text"],
          "description": "Short description of the article",
          "moduleConfig": {
            "text2vec-transformers": {
              "skip": True,
            },
          },
        },
        {
          "name": "description",
          "dataType": ["text"],
          "description": "Description of the article"
        },
        {
          "name": "keywords",
          "dataType": ["text[]"],
          "description": "Keywords of the article",
          "moduleConfig": {
            "text2vec-transformers": {
              "skip": True,
            },
          },
        },
        {
          "name": "descriptionWordCount",
          "dataType": ["int"],
          "description": "Number of words in description",
        },
        {
          "name": "hasAuthors",
          "dataType": ["Author"],
          "description": "The authors this article has"
        }
      ]
    },
    {
      "class": "Author",
      "description": "An Author class to store the author information",
      "properties": [
        {
          "name": "name",
          "dataType": ["string"],
          "description": "The name of the author",
          "moduleConfig": {
            "text2vec-transformers": {
              "skip": True,
            },
          },
        },
        {
          "name": "hasArticles",
          "dataType": ["Article"],
          "description": "The articles of the author"
          }
      ]
    }
  ]
}
