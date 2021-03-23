"""
Controllers for visionhub-cli. Main bussines logic
"""

from pathlib import Path
import os

import requests
import docker
import click

from .config_processor import (
    construct_model_config_from_prompt,
    write_config,
    read_config,
)
from .utils import exception_handler


@exception_handler
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


@exception_handler
def create(result_config_path: Path):
    """
    Request required fields from user to create config
    """

    model_config = construct_model_config_from_prompt()
    write_config(result_config_path, model_config)


@exception_handler
def build(directory: Path, config_path: Path):
    """
    Build docker image and tag it with config["slug"] and version config["version"]
    """

    config = read_config(config_path)

    if not config.slug or not config.link:
        raise ValueError("Config must contain slug and link")

    try:
        cli = docker.from_env().api
    except docker.errors.DockerException:
        click.echo("You should start docker firstly")
        return
    for response in cli.build(path=str(directory), tag=config.link, decode=True):
        if "stream" in response and response["stream"] != "\n":
            click.echo(response["stream"])
    click.echo(f"Built image and tagged {config.link} 📦")


@exception_handler
def test(config_path: Path) -> bool:
    config = read_config(config_path)
    link = config.link
    try:
        cli = docker.from_env()
    except docker.errors.DockerException:
        click.echo("You should start docker firstly")
        return
    try:
        logs = cli.containers.run(
            image=link,
            detach=False,
            stderr=True,
            environment={"TEST_MODE": 1, "BATCH_SIZE": 1},
        )
    except docker.errors.ContainerError as e:
        click.echo("Container return error 😵")
        click.echo(e.stderr)
        return False

    click.echo(logs)
    click.echo("Test passed ✅")
    return True


@exception_handler
def push(config_path: Path):
    """
    Push image that to registry
    """

    cli = docker.from_env()

    config = read_config(config_path)
    if not config.slug or not config.link:
        raise ValueError("Config must contain slug and link fields")

    repository = config.link.split(":")[0]
    tag = config.link.split(":")[1]

    click.echo("Pushing...")
    cli.images.push(repository, tag=tag)
    click.echo(f"Image pushed {config.link} 🚀")


@exception_handler
def deploy(address: str, config_path: Path):
    """
    Deploy model to the visionhub platform
    """

    try:
        with open(f".visionhub/{address.split('://')[1]}", "r") as f:
            token = f.read().split(",")[1]
    except FileNotFoundError:
        raise ValueError(
            "You are not loggined. Firstly you should call visionhub-cli login"
        )

    config = read_config(config_path)

    data = config.dict()
    files = {}
    for field in config.dict():
        if isinstance(data[field], str) and os.path.isfile(data[field]):
            files[field] = open(data.pop(field), "rb")

    for field in config.dict():
        if isinstance(data[field], Path) and os.path.isfile(data[field]):
            files[field] = open(data[field], "rb")
        if field == "supported_modes":
            data[field] = list(map(lambda x: x.value, data[field]))

    data.pop("version")

    click.echo("Check is model is already deployet")
    response = requests.get(
        address + f"/api/frontend/model/{config.slug}/",
        headers={"Authorization": "Token " + token},
    )
    is_create = response.status_code == 404
    click.echo(f"Model is presented in visionhub platform {not is_create}")
    method = "post" if is_create else "patch"
    uri = address + "/api/frontend/model/" + ("" if is_create else config.slug + "/")
    response = requests.request(
        method,
        uri,
        data=data,
        files=files,
        headers={"Authorization": "Token " + token},
    )
    if response.status_code not in (201, 200):
        try:
            json = response.json()
            raise ValueError(response.json())
        except Exception:
            with open(".visionhub/log", "ab") as file_:
                file_.write(response.content)
            raise ValueError("Visionhub returns error writed to .visionhub/log")

    for _file in files.values():
        _file.close()
    click.echo(f"Deployet at {address}/api/frontend/model/{config.slug} 🚀")
