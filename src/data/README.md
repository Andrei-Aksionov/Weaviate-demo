# WEAVIATE DATA LOADING

Data loading is described in:

- How to load data from [official documentation](https://weaviate.io/developers/weaviate/current/tutorials/how-to-import-data.html)
- What is batch from [official documentation](https://weaviate.io/developers/weaviate/current/restful-api-references/batch.html#batch-references)
- Examples with different options of batch creation are shown in this [article](https://towardsdatascience.com/getting-started-with-weaviate-python-client-e85d14f19e4f)

***

## How data can be loaded with functions

In our case we have two classes:

- Article
- Author

Each class has reference to each other.

So in order to load data we need to create 3 functions:

1. Function for adding article to batch.
It prepares dictionary with keys identical to names of properties of class Article and adds it to the batch. For example:

    ```python
    def add_article(batch: weaviate.client.Batch, data: dict) -> str:
        article_object = {
            "property_name": "value",
            ...
        }
        id = batch.add_data_object(
            class_name="Article",
            data_object=article_object,
        )
        return id
    ```

    Id will be used later during reference creation.

2. Function for adding author to batch. Basically the same as for adding articles:

    ```python
    def add_author(batch: weaviate.client.Batch, data: dict) -> str:
        author_object = {
            "property_name": "value",
            ...
        }
        id = batch.add_data_object(
            class_name="Author",
            data_object=author_object,
        )
        return id
    ```

3. Function thats adds reference to batch. As in case of this project each article references to it's author and each author references to written articles , so cross-references have to be created:

    ```python
    def add_reference(batch: weaviate.client.Batch, article_id: str, author_id: str) -> None:
        # author -> article
        batch.add_reference(
            from_object_uuid=author_id,
            from_object_class_name="Author",
            from_property_name="hasArticles",
            to_object_uuid=article_id,
        )
        # article -> author
        batch.add_reference(
            from_object_uuid=article_id,
            from_object_class_name="Article",
            from_property_name="hasAuthors",
            to_object_uuid=author_id,
        )
    ```

4. The last step is to iteratively add data to batch:

    ```python
    for data_object in data:
        article_id = add_author(batch, data_object)
        author_id = add_author(batch, data_object)
        add_reference(batch, article_id, author_id)
    ```

That's basically it. The only this is missing is to choose what approach of batch creation is to choose from (manual or automatic). Links with description of batch creation options are listed at the top of this file.

***

**Quick note**: some authors are mentioned in multiple articles (reused between them), so there is no need to create new object of class Author if it is already in Weaviate instance. Duplicated authors will be dropped automatically by Weaviate, but by adding to batch such authors it will slow down the loading process. So it might be a good idea to generate manually uuid for each author object and check in local `set` variable if it is already exist. If it's so do not add this object to batch and just return this uuid which later will be used for adding reference.

For example something like this:

```python
created_authors = set()

for data_object in data:
    article_id = add_author(batch, data_object)
    author_id = generate_uuid(("Author", data_object["author_name"], ...))
    if author_id not in created_authors:
        created_authors.add(author_id)
        author_id = add_author(batch, data_object)
    add_reference(batch, article_id, author_id)
```

## WeaviateDataLoader

Manual approach is easy to understand but the problem with it is that with each change in schema file all these three functions has to be changed. And if there are even more classes with different references then it might be tedious to create functions for all classes. That's why in file "data_loader.py" you can find "WeaviateDataLoader" class that parses schema file and according to it automatically adds data_objects and references for each class.

WeaviateDataLoader's `.load()` method expects a dictionary with keys in special format:

- keys has to be in form: [class_name]_[property_name], e.g. article_title, article_url, author_name and so on. It is required because different classes might have the same property name.

Example of how to load data is shown in `main.py` file. Use it as a reference.
