"""
Controllers for visionhub-cli. Main bussines logic
"""

from pathlib import Path

import click

from .config_processor import (
    read_field_templates,
    write_config,
    Field,
)


def create(result_config_path: Path):
    """
    Request required fields from user to create config
    """
    field_templates = read_field_templates(
        Path("visionhub-cli/src/config-template.yaml")
    )
    fields = []
    for field_template in field_templates:
        if field_template.required and field_template.default is None:
            value = click.prompt(field_template.description, type=str)
        else:
            value = click.prompt(
                field_template.description,
                type=str,
                default=field_template.default
                if field_template.default is not None
                else "",
            )

        fields += [Field.parse_string(field_template, value)]

    write_config(result_config_path, fields)
