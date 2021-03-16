"""
Controllers for visionhub-cli. Main bussines logic
"""

from pathlib import Path
import os

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
    with open(f".visionhub/{address.split('://')[1]}", "w") as f:
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

        if value == "":
            continue

        fields += [Field.parse_string(field_template, value)]

    write_config(result_config_path, fields)


def build(directory: Path, config_path: Path):
    """
    Build docker image and tag it with config["slug"] and version config["version"]
    """

    config = read_config(config_path)

    if "slug" not in config or "version" not in config:
        raise ValueError("Config must contain slug and version fields")

    cli = docker.from_env().api
    filepath = directory / "Dockerfile"
    fileobj = open(filepath, "rb")
    for response in cli.build(
        fileobj=fileobj, tag=config["link"] + ":" + config["version"], decode=True
    ):
        if "stream" in response and response["stream"] != "\n":
            click.echo(response["stream"])
    click.echo(f"Built image and tagged {config['link']}:{config['version']}")


def push(config_path: Path):
    """
    Push image that to registry
    """

    cli = docker.from_env()

    config = read_config(config_path)
    if "slug" not in config or "version" not in config:
        raise ValueError("Config must contain slug and version fields")

    repository = config["link"]
    tag = config["version"]

    click.echo("Pushing...")
    cli.images.push(repository, tag=tag)
    click.echo(f"Image pushed {config['link']}:{config['version']}")


def deploy(address: str, config_path: Path):
    """
    Deploy model to the visionhub platform
    """

    try:
        with open(f".visionhub/{address.split('://')[1]}", "r") as f:
            token = f.read().split(",")[1]
    except FileNotFoundError as exc:
        raise ValueError(
            "You are not loggined. Firstly you should call visionhub-cli login"
        ) from exc

    config = read_config(config_path)

    data = {}
    files = {}
    for field in config:
        if isinstance(config[field], str) and os.path.isfile(config[field]):
            files[field] = open(config[field], "rb")
        elif field == "link":
            data[field] = config[field] + config["version"]
        else:
            data[field] = config[field]

    data.pop("version")
    data["supported_modes"] = data.pop("modes")

    response = requests.get(
        address + f"/api/frontend/model/{data['slug']}/",
        headers={"Authorization": "Token " + token},
    )
    is_create = response.status_code == 404
    method = "post" if is_create else "patch"
    uri = (
        address + "/api/frontend/model/" + ("" if is_create else data.pop("slug") + "/")
    )
    response = requests.request(
        method,
        uri,
        data=data,
        files=files,
        headers={"Authorization": "Token " + token},
    )
    if response.status_code not in (201, 200):
        raise ValueError(response.json())
    click.echo(f"Deployet at {address}/api/frontend/model/{config['slug']}")
