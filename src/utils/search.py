from typing import Optional

from termcolor import colored


def pprint_response(response: dict, description_size_limit: Optional[int] = 500) -> None:
    """Prints response in a prettier way.

    Parameters
    ----------
    response : dict
    description_size_limit : Optional[int], optional
        if set "descripton" and "short_description" will be limited to that amount, by default 500
    """
    response = response["data"]["Get"]

    for class_name in response:
        print(colored(class_name.upper(), "red", "on_white", attrs=["bold"]))

        for idx, resp in enumerate(response[class_name]):
            print(f"Response # {idx}")
            for key, value in resp.items():
                if key in {"description", "short_description"} and description_size_limit:
                    value = value[:description_size_limit]
                print(f"{colored(key, 'magenta', 'on_grey')}: {value}")
            print("=" * 120)
