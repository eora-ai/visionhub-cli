"""
CRUD class for config.

config format: config_template.yaml
"""

from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional, Dict

import yaml


class ValueType(Enum):
    STR = "str"
    PATH = "path"
    INT = "int"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ARRAY = "array[str]"


CONSTRUCTORS = {
    ValueType.STR: str,
    ValueType.PATH: Path,
    ValueType.INT: int,
    ValueType.FLOAT: float,
    ValueType.BOOLEAN: lambda value: value == "y",
    ValueType.ARRAY: lambda value: list(map(str.strip, value.split(","))),
}


@dataclass
class FieldTemplate:
    name: str
    description: str
    value_types: List[ValueType]
    required: bool = True
    default: Optional[str] = None


@dataclass
class Field:
    template: FieldTemplate
    value: Any

    @classmethod
    def parse_string(cls, template: FieldTemplate, value: str):
        processed_value = None
        for value_type in template.value_types:
            try:
                processed_value = CONSTRUCTORS[value_type](value)
            except ValueError:
                continue
            break
        else:
            raise ValueError(
                f"Wrong format for {value} try to parse using {template.value_types}"
            )
        return cls(template, processed_value)


def config_dictionary_to_field_templates(template_dict: dict) -> List[FieldTemplate]:
    """
    Make list of FieldTemplate out of config dictionary.

    Parameters
    ----------
    template_dict:
        Template dict of format {name: {"description": str, "type": str}}
    """
    field_templates = []
    for name in template_dict:
        value_types = list(
            map(ValueType, map(str.strip, template_dict[name]["type"].split("|")))
        )
        field_template = FieldTemplate(
            name=name,
            description=template_dict[name]["description"],
            value_types=value_types,
            required=template_dict[name].get("required", True),
            default=template_dict[name].get("default", None),
        )
        field_templates += [field_template]
    return field_templates


def read_field_templates(template_path: Path) -> List[FieldTemplate]:
    with open(template_path) as template_file:
        template_dict = yaml.full_load(template_file)
    return config_dictionary_to_field_templates(template_dict)


def fields_to_dict(fields: List[Field]) -> Dict[str, Any]:
    """
    Convert list of fields into dict
    """
    return {
        field.template.name: field.value
        if not isinstance(field.value, Path)
        else str(field.value)
        for field in fields
    }


def write_config(config_path: Path, fields: List[Field]):
    """
    Convert fields into dict and wrte it on the disk
    """
    fields_dict = fields_to_dict(fields)

    with open(config_path, "w") as config_file:
        yaml.dump(fields_dict, config_file, sort_keys=False)

def read_config(config_path: Path) -> dict:
    with open(config_path, "r") as config_file:
        config = yaml.full_load(config_file)
    return config
