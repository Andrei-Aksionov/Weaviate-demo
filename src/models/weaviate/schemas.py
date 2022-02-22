combined_class_schema = {
    "classes": [
        {
            "class": "Article",
            # a description of what this class represents
            "description": "An Article class to store the article summary and its authors",
            # class properties
            "properties": [
                {
                    "name": "title",
                    "dataType": ["string"],
                    "description": "The title of the article",
                },
                {
                    "name": "summary",
                    "dataType": ["text"],
                    "description": "The summary of the article",
                },
                {
                    "name": "hasAuthors",
                    "dataType": ["Author"],
                    "description": "The authors this article has",
                },
            ],
            "vectorizer": "none",
        },
        {
            "class": "Author",
            "description": "An Author class to store the author information",
            "properties": [
                {
                    "name": "name",
                    "dataType": ["string"],
                    "description": "The name of the author",
                },
                {
                    "name": "wroteArticles",
                    "dataType": ["Article"],
                    "description": "The articles of the author",
                },
            ],
        },
    ]
}
