from typing import Tuple, Dict, List, Any


def quoted(string: str) -> str:
    """ Returns the given string wrapped in escaped double quotes. """
    return f"\"{string}\""


def get_dict_with_element(dict_list: List[Dict], key: Any, value: Any) -> Dict:
    """ Returns the first dictionary whose key/value pair corresponds
        to the given arguments, or None if none was found.
    """
    return (next((d for d in dict_list if d.get(key) == value), None))


def get_dict_with_element_in_list(dict_list: List[Dict], key: Any, values: List) -> Dict:
    """ Returns the first dictionary those whose `key` corresponds to one
        of the given `values`, or None if none was found.
    """
    for value in values:
        found_dict = get_dict_with_element(dict_list, key, value)
        if found_dict is not None:
            return found_dict
    return None


def get_dicts_with_element(dict_list: List[Dict], key: Any, value: Any) -> List[Dict]:
    """ Filters the dictionaries and returns those whose key/value pair
        corresponds to the given arguments.
    """
    return [d for d in dict_list if d.get(key) == value]


def get_dicts_with_element_in_list(dict_list: List[Dict], key: Any,
        values: List) -> List[Dict]:
    """ Filters the dictionaries and returns only those whose `key` corresponds
        to one of the given `values`.
    """
    all_filtered_dicts = []

    for value in values:
        all_filtered_dicts += get_dicts_with_element(dict_list, key, value)
    
    return all_filtered_dicts
    