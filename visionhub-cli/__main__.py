"""
Entrypoint of visionhub-cli
"""
from typing import Optional

import click

VERSION = "0.0.1"


@click.group()
@click.version_option(VERSION)
def main():
    """
    CLI for the visionhub platform. The main goal is to automate build and deploy models.
    """


@main.command()
@click.option("-t", "--token", "token")
def login(token: Optional[str]):
    """
    This command request a token, check it and save it to ~/.visionhub-cli/token
    """
    if token is not None:
        click.echo("This is not save to populate token not from stdin")


@main.command()
@click.argument("directory", required=False, default=".")
@click.argument("config_file", required=False, default="visionhub-model.yaml")
def create(directory: Optional[str], config_file: Optional[str]):
    """
    Make configuration file for release
    """


@main.command()
@click.argument("directory", required=False, default=".")
@click.argument("config_file", required=False, default="visionhub-model.yaml")
def release(directory: Optional[str], config_file: Optional[str]):
    """
    Build model and push results to the docker registry
    """


@main.command()
@click.argument("directory", required=False, default=".")
@click.argument("config_file", required=False, default="visionhub-model.yaml")
def build(directory: Optional[str], config_file: Optional[str]):
    """
    Build model using `docker build`
    """


@main.command()
@click.argument("config_file", required=False, default="visionhub-model.yaml")
def push(config_file: Optional[str]):
    """
    Push model to the docker registry
    """


@main.command()
@click.argument("config_file", required=False, default="visionhub-model.yaml")
def deploy(config_file: Optional[str]):
    """
    Deploy model to the visionhub platform
    """


if __name__ == "__main__":
    main()
