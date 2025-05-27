from enum import Enum

def str_to_enum(string: str, enum_value: type[Enum] | list[type[Enum]]) -> Enum:
    if not isinstance(enum_value, list):
        for enum_string in enum_value:
            if enum_string.value == string:
                return enum_string

    else:
        for sub_enum in enum_value:
            for enum_string in sub_enum:
                if enum_string.value == string:
                    return enum_string

    raise ValueError(f"Invalid enum value: {string}")