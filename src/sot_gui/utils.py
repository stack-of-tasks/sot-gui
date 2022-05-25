from typing import Tuple, Dict, List, Any


def quoted(string: str) -> str:
    """ Returns the given string wrapped in escaped double quotes. """
    return f"\"{string}\""


def filter_dicts_per_attribute(dict_list: List[Dict], key: Any, value: Any) -> List[Dict]:
    """ Filters the dictionaries and returns those whose key/value pair
        corresponds to the given arguments.
    """
    return list(filter(lambda dict: dict[key] == value, dict_list))