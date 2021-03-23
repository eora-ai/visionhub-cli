"""
Model config processor using pydantic
"""

from typing import Any
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic.fields import ModelField
import click


def link_completion(ctx: dict, default: Any):
    """
    Make link out of slug and version
    """
    return (
        "public.registry.visionhub.ru/models/"
        + ctx["inputs"]["slug"]
        + ":"
        + ctx["inputs"]["version"]
    )


class ModelConfig(BaseModel):
    """
    Class of model config
    """

    slug: str = Field(required=True, description="Uniq name of the model")
    name: str = Field(required=True, description="Descriptive name of the model")
    anons: str = Field(required=True, description="Short description of the model")
    description: str = Field(required=True, description="Long description of the model")
    md_documentation: Path = Field(
        required=True,
        default="README.md",
        description="Path to the md file with documentation",
    )
    version: str = Field(
        required=False, default="v4", description="Version of the model"
    )
    link: str = Field(
        required=False,
        description="Link to docker address",
        completion=link_completion,
    )


def model_field_prompt(model_field: ModelField, ctx: dict) -> Any:
    completion = lambda ctx, x: x
    if "completion" in model_field.field_info.extra:
        completion = model_field.field_info.extra["completion"]
    return click.prompt(
        model_field.field_info.description,
        default=completion(ctx, model_field.default),
        type=model_field.type_,
    )


def construct_model_config_from_prompt() -> ModelConfig:
    ctx = {"inputs": {}}
    for _, field in ModelConfig.__fields__.items():
        ctx["inputs"][field.alias] = model_field_prompt(field, ctx)

    model_config = ModelConfig(**ctx["inputs"])
    click.echo(model_config)
