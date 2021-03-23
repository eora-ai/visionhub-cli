"""
Model config processor using pydantic
"""

import os
from typing import Any, List, Callable, Optional, Union
from pathlib import Path
from enum import Enum

import yaml
from pydantic import BaseModel, Field
from pydantic.fields import ModelField
import click

from .exceptions import FieldNotNeeded


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


def check_need(*modes) -> Callable[[dict], bool]:
    def __check_nedded(ctx: dict) -> bool:
        return any(map(lambda mode: mode in modes, ctx["inputs"]["modes"]))

    return __check_nedded


class Modes(Enum):
    IMG2IMG = "IMG2IMG"
    IMG2VID = "IMG2VID"
    VID2IMG = "VID2IMG"
    VID2VID = "VID2VID"


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
    supported_modes: List[Modes] = Field(
        required=True,
        alias="modes",
        description="multiple of [IMG2IMG, IMG2VID, VID2IMG, VID2VID], separated by comma",
        parse_str=lambda x: x.split(","),
    )
    preview: Path = Field(required=True, description="Path to preview image")
    image_input_example: Optional[Path] = Field(
        required=False,
        description="Path to image input example",
        check_need_func=check_need("IMG2IMG", "IMG2VID"),
    )
    image_output_example: Optional[Path] = Field(
        required=False,
        description="Path to image output example",
        check_need_func=check_need("IMG2IMG", "VID2IMG"),
    )
    video_input_example: Optional[Path] = Field(
        required=False,
        description="Path to video input example",
        check_need_func=check_need("VID2IMG", "VID2VID"),
    )
    video_output_example: Optional[Path] = Field(
        required=False,
        description="Path to video output example",
        check_need_func=check_need("IMG2VID", "VID2VID"),
    )
    cost_for_image_to_image: Optional[float] = Field(
        required=False,
        description="Cost of one image",
        check_need_func=check_need("IMG2IMG"),
        default_if_needed=1,
    )
    cost_for_image_to_video: Optional[float] = Field(
        required=False,
        description="Cost of one image that will converted to video",
        check_need_func=check_need("IMG2VID"),
        default_if_needed=10,
    )
    cost_for_video_to_image: Optional[float] = Field(
        required=False,
        description="Cost of one second of video that will converted to image",
        check_need_func=check_need("VID2IMG"),
        default_if_needed=10,
    )
    cost_for_video_to_video: Optional[float] = Field(
        required=False,
        description="Cost of one second of video",
        check_need_func=check_need("VDI2VID"),
        default_if_needed=10,
    )
    without_meta: bool = Field(
        required=True,
        description="Can be run without meta",
        parse_str=lambda x: x == "y",
    )
    is_private: bool = Field(
        required=True,
        description="Is it private model",
        parse_str=lambda x: x == "y",
    )
    gpu: bool = Field(
        required=True,
        description="Does the model require GPU for running?",
        parse_str=lambda x: x == "y",
    )
    batch_size: int = Field(
        required=True,
        description="Maximum batch size that can fit to 13Gb of GPU memory",
    )
    meta_template: Union[str, Path] = Field(
        default="{}",
        required=False,
        description="Json template for the meta(https://json-schema.org) (path or str)",
        parse_str=lambda x: x if not os.path.isfile(x) else Path(x),
    )
    meta_input_example: Union[str, Path] = Field(
        default="{}",
        required=False,
        description="Example of meta information",
        parse_str=lambda x: x if not os.path.isfile(x) else Path(x),
    )
    prediction_example: Union[str, Path] = Field(
        required=True,
        description="Json example of result",
        parse_str=lambda x: x if not os.path.isfile(x) else Path(x),
    )


def model_field_prompt(model_field: ModelField, ctx: dict) -> Any:
    if "check_need_func" in model_field.field_info.extra:
        check_need_func = model_field.field_info.extra["check_need_func"]
        if not check_need_func(ctx):
            raise FieldNotNeeded(model_field)
    if "default_if_needed" in model_field.field_info.extra:
        return model_field.field_info.extra["default_if_needed"]
    completion = lambda ctx, x: x
    if "completion" in model_field.field_info.extra:
        completion = model_field.field_info.extra["completion"]
    type_ = model_field.type_
    parse_str = lambda x: x
    if "parse_str" in model_field.field_info.extra:
        type_ = str
        parse_str = model_field.field_info.extra["parse_str"]
    return parse_str(
        click.prompt(
            model_field.field_info.description,
            default=completion(ctx, model_field.default),
            type=type_,
        )
    )


def construct_model_config_from_prompt() -> ModelConfig:
    ctx = {"inputs": {}}
    for _, field in ModelConfig.__fields__.items():
        try:
            ctx["inputs"][field.alias] = model_field_prompt(field, ctx)
        except FieldNotNeeded:
            continue

    return ModelConfig(**ctx["inputs"])


def write_config(result_config_path: Path, model_config: ModelConfig):
    model_config_dict = model_config.dict()
    model_config_dict = {
        key: value for key, value in model_config_dict.items() if not value is None
    }
    for key in model_config_dict:
        if isinstance(model_config_dict[key], Path):
            model_config_dict[key] = str(model_config_dict[key])
        if isinstance(model_config_dict[key], list):
            model_config_dict[key] = list(
                map(lambda x: x.value, model_config_dict[key])
            )

    with open(result_config_path, "w") as file_:
        yaml.dump(model_config_dict, file_)
        click.echo(f"Config writed to {result_config_path}")


def read_config(config_path: Path) -> ModelConfig:
    with open(config_path, "r") as file_:
        model_dict = yaml.full_load(file_)
        return ModelConfig(**model_dict)
