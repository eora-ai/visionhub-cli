"""
Controllers for visionhub-cli. Main bussines logic
"""

from pathlib import Path

import requests
import docker
import click

from .config_processor import (
    read_field_templates,
    read_config,
    write_config,
    Field,
)


def login(token: str, address: str):
    """
    Check token, save to ~/.visionhub/tokens
    """

    resp = requests.get(
        address + "/api/frontend/user/", headers={"Authorization": "Token " + token}
    )
    if not resp.ok:
        raise ValueError("Token is incorrect")

    # save token
    Path(".visionhub").mkdir(exist_ok=True)
    with open(".visionhub/token", "w") as f:
        f.write(f"{address},{token}")


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


def build(directory: Path, config_path: Path):
    """
    Build docker image and tag it with config["slug"] and version config["version"]
    """

    config = read_config(config_path)

    if "slug" not in config or "version" not in config:
        raise ValueError("Config must contain slug and version fields")

    cli = docker.APIClient(base_url='unix://var/run/docker.sock')
    filepath = directory / "Dockerfile"
    fileobj = open(filepath, "rb")
    for response in cli.build(fileobj=fileobj, tag=config["link"] + ":" + config["version"], decode=True):
        if "stream" in response and response["stream"] != "\n":
            click.echo(response["stream"])
    click.echo(f"Built image and tagged {config['link']}:{config['version']}")
