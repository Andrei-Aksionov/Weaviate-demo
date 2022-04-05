from typing import Any, Sequence


def split_string(text: str, delimeter: str = ",", strip: bool = True) -> list[str]:
    """Splits string with specified delimeter.

    Parameters
    ----------
    text : str
        string containing text
    delimeter : str, optional
        by this delimeter string will be splitter into tokens, by default ","
    strip : bool, optional
        if True empty spaces in the begginning and the end of each token will be striped, by default True

    Returns
    -------
    list[str]
        list with tokens of splitted string
    """
    tokens = text.split(delimeter)
    if not strip:
        return tokens
    return [t.strip() for t in tokens]


def ravel(data: Sequence) -> Any:
    """Returns the first element of sequence object with only one element.

    Besides convenience this function lets you to be sure that in provided sequence object
    there are only one element. So no more guessing when you see someting like:
    ```python
        data[0]
    ```
    whether there are multiple elements and code's author decided to take for some reason only
    the first element, or there are only one element at all.

    Parameters
    ----------
    data : Sequence
        sequence object with only one element

    Returns
    -------
    Any
        the first element of sequence object

    Raises
    ------
    ValueError
        if sequence object contains more than one element
    """
    if (data_len := len(data)) != 1:
        raise ValueError(f"Expected sequence with len of 1, actually got with len of {data_len}")
    return data[0]
