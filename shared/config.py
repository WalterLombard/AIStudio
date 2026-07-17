from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel


ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = ROOT / "config" / "config.yaml"


class ApplicationConfig(BaseModel):
    name: str
    version: str


class PathsConfig(BaseModel):
    projects: str
    logs: str
    cache: str
    prompts: str
    schemas: str
    assets: str
    templates: str


class LLMConfig(BaseModel):
    provider: str
    model: str


class ImageConfig(BaseModel):
    provider: str
    model: str


class VideoConfig(BaseModel):
    provider: str
    model: str


class ModelsConfig(BaseModel):
    llm: LLMConfig
    image: ImageConfig
    video: VideoConfig


class LoggingConfig(BaseModel):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"]


class Config(BaseModel):
    application: ApplicationConfig
    paths: PathsConfig
    models: ModelsConfig
    logging: LoggingConfig


with open(CONFIG_FILE, "r", encoding="utf-8") as file:
    config = Config(**yaml.safe_load(file))