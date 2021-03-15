"""
Entrypoint of visionhub-cli
"""
import click

VERSION = "0.0.1"


@click.group()
@click.version_option(VERSION)
def main():
    """
    CLI for the visionhub platform. The main goal is to automate build and deploy models.
    """


@main.command()
@click.argument("directory", required=False, default=".")
@click.argument("config_file", required=False, default="visionhub-model.yaml")
def create(directory: str, config_file: str):
    """
    Make configuration file for release
    """


@main.command()
@click.argument("directory", required=False, default=".")
@click.argument("config_file", required=False, default="visionhub-model.yaml")
def release(directory: str, config_file: str):
    """
    Build model and push results to the docker registry
    """


@main.command()
@click.argument("directory", required=False, default=".")
@click.argument("config_file", required=False, default="visionhub-model.yaml")
def build(directory: str, config_file: str):
    """
    Build model using `docker build`
    """


@main.command()
@click.argument("config_file", required=False, default="visionhub-model.yaml")
def push(config_file: str):
    """
    Push model to the docker registry
    """


@main.command()
@click.argument("config_file", required=False, default="visionhub-model.yaml")
def deploy(config_file: str):
    """
    Deploy model to the visionhub platform
    """


if __name__ == "__main__":
    main()
