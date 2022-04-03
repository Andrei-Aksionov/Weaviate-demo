# WEAVIATE SCHEMA

> "A schema is used to define the concepts of the data you will be adding to Weaviate."

## TODO: finalize this readme file

Basically in schema we can specify what classes are used, what properties each class has and optionally we can specify relations between different classes.

Examples of how to add schema:

- [Official documentation](https://weaviate.io/developers/weaviate/current/tutorials/how-to-create-a-schema.html)
- [Article](https://hackernoon.com/what-is-weaviate-and-how-to-create-data-schemas-in-it-7hy3460) with example of classes with multiple references

## CLASSES

For example in this project [CNBC dataset](https://data.world/crawlfeeds/cnbc-news-dataset) is used that we can split into two classes:

- Article
- Author

## PROPERTIES

Each class has it's own set of properties:

- Article has:
  - title
  - url
  - publish date
  - who is the author
  - 2 variants of descriptions
  - set of keywords
- Author has:
  - name

These two classes are related to each other. Articles has property "hasAuthors" which stores link to it's author, and Authors has property "hasArticles" - link to written articles.

## DATA TYPES

Each property has it's own data type. List of types is described [here](https://weaviate.io/developers/weaviate/current/data-schema/datatypes.html). Properties that contains reference to other classes has data type of referenced class:

- hasAuthors data type is Author
- hasArticles data type is Article

## VECTORIZATION

With [text2vec-transformers](https://weaviate.io/developers/weaviate/current/retriever-vectorizer-modules/text2vec-transformers.html) module Weaviate for each class  concatenates **all text** properties, sends it to vectorization module and use this vector during vector search.

That's why if you want to exclude any properties from vectorization process you can provide skip parameter:

```json
"moduleConfig": {
    "text2vec-transformers": {
        "skip": true
    }
}
```

In "schema.json" file you can notices that vectorization is disabled for:

- url: vector of url will only add noise
- short_description: it's basically shorten version of description, only vector for description is used
- keywords: in my opinion it's not helpful but I might be wrong
- name of the author: that's definitely will not help

As a reminder: from what I noticed during debugging custom text2vec-transformers module Weaviate doesn't vectorize each text property separately and then takes mean value of them, but rather concatenates all text properties, vectorizes this string and attaches this vector to the object of class (in our case each article). Then this vector is used during vector search. **So be careful what properties to include into vector representation of document**.

Other properties are not string or text data types so they are not used for vectorization.
