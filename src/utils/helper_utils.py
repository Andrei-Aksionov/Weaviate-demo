from typing import Any, Iterable

from weaviate import Client


def split_string(text: str, delimeter: str = ",") -> list[str]:
    return [w.strip() for w in text.split(delimeter)]


def ravel(data: Iterable) -> Any:
    """Returns the first element (data should contain only one element)

    TODO: finish docstring
    Parameters
    ----------
    data : Iterable
        _description_

    Returns
    -------
    Any
        _description_

    Raises
    ------
    ValueError
        _description_
    """
    if len(data) != 1:
        raise ValueError(f"Expected iterable with len of 1, actually got with len of {len(data)}")
    return data[0]


def add_schema(client: Client, schema: dict, delete_all: bool = True) -> None:
    if delete_all:
        client.schema.delete_all()
    client.schema.create(schema)
