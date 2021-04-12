"""
Entrypoint of visionhub-cli
"""
from typing import Optional
from pathlib import Path

import click

from .src import controllers

VERSION = "0.2.7"


@click.group()
@click.version_option(VERSION)
def main():
    """
    CLI for the visionhub platform. The main goal is to automate build and deploy models.
    """


@main.command()
@click.option("-t", "--token", "token")
@click.option("-a", "--address", default="https://api.visionhub.ru")
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
    click.echo("Run tests ...")
    if not controllers.test(config_file):
        click.echo("You cannot push model if test are failed")
        return
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
def test(config_file: Optional[str]):
    """
    Build model using `docker build`
    """
    controllers.test(Path(config_file))


@main.command()
@click.argument("config_file", required=False, default=".visionhub/model.yaml")
def push(config_file: Optional[str]):
    """
    Push model to the docker registry
    """
    click.echo("Run tests ...")
    if not controllers.test(config_file):
        click.echo("You cannot push model if test are failed")
        return
    controllers.push(Path(config_file))


@main.command()
@click.argument("config_file", required=False, default=".visionhub/model.yaml")
@click.option("-a", "--address", default="https://api.visionhub.ru")
def deploy(config_file: Optional[str], address: str):
    """
    Deploy model to the visionhub platform
    """
    click.echo("Run tests ...")
    if not controllers.test(config_file):
        click.echo("You cannot push model if test are failed")
        return
    controllers.deploy(address, Path(config_file))


if __name__ == "__main__":
    main()
