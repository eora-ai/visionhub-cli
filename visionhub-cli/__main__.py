"""
Entrypoint of visionhub-cli
"""
from typing import Optional
from pathlib import Path

import click

import src.controllers as controllers

VERSION = "0.0.1"


@click.group()
@click.version_option(VERSION)
def main():
    """
    CLI for the visionhub platform. The main goal is to automate build and deploy models.
    """


@main.command()
@click.option("-t", "--token", "token")
@click.option("-a", "--address")
def login(token: Optional[str], address: str = "https://api.visionhub.ru"):
    """
    This command request a token, check it and save it to ~/.visionhub-cli/tokens
    """
    if token is not None:
        click.echo("This is not save to populate token not from stdin")
    else:
        token = click.prompt("Token", type=str)
    controllers.login(token, address)


@main.command()
@click.argument("config_file", required=False, default=".visionhub/model.yaml")
def create(config_file: str):
    """
    Make configuration file for release
    """
    controllers.create(Path(config_file))


@main.command()
@click.argument("directory", required=False, default=".")
@click.argument("config_file", required=False, default=".visionhub/model.yaml")
@click.option("-a", "--address", default="https://api.visionhub.ru")
def release(address: str, directory: Optional[str], config_file: Optional[str]):
    """
    Build model and push results to the docker registry
    """
    controllers.build(Path(directory), Path(config_file))
    controllers.push(Path(config_file))
    controllers.deploy(address, Path(config_file))


@main.command()
@click.argument("directory", required=False, default=".")
@click.argument("config_file", required=False, default=".visionhub/model.yaml")
def build(directory: Optional[str], config_file: Optional[str]):
    """
    Build model using `docker build`
    """
    controllers.build(Path(directory), Path(config_file))


@main.command()
@click.argument("config_file", required=False, default=".visionhub/model.yaml")
def push(config_file: Optional[str]):
    """
    Push model to the docker registry
    """
    controllers.push(Path(config_file))


@main.command()
@click.argument("config_file", required=False, default=".visionhub/model.yaml")
@click.option("-a", "--address", default="https://api.visionhub.ru")
def deploy(config_file: Optional[str], address: str):
    """
    Deploy model to the visionhub platform
    """
    controllers.deploy(address, Path(config_file))


if __name__ == "__main__":
    main()
