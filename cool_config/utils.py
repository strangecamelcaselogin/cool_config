from typing import Union


def str_is_bool(value: str) -> bool:
    return value == 'True' or value == 'False'


def str2bool(value: str) -> bool:
    return value == 'True'


def deserialize_if_possible(value: str) -> Union[float, int, bool, str]:
    try:
        value = float(value)
        if value.is_integer():
            value = int(value)
    except ValueError:
        if str_is_bool(value):
            value = str2bool(value)

    return value
