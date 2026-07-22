"""
AIStudio Configuration Loader

Loads application and model configuration from YAML settings.

Author : AIStudio
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel

from shared.exceptions import ConfigurationError


# ==========================================================
# Configuration File Location
# ==========================================================

ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = ROOT / "config" / "config.yaml"


# ==========================================================
# Application Configuration Models
# ==========================================================

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
    endpoint: str
    temperature: float
    num_predict: int


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
    level: Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
    ]


class Config(BaseModel):
    application: ApplicationConfig
    paths: PathsConfig
    models: ModelsConfig
    logging: LoggingConfig


# ==========================================================
# Load Configuration Function
# ==========================================================

def load_config(config_path: Path = CONFIG_FILE) -> Config:
    """Loads and validates the configuration file."""
    if not config_path.exists():
        raise ConfigurationError(
            f"Configuration file not found at: {config_path}"
        )

    try:
        with open(config_path, "r", encoding="utf-8") as file:
            raw_yaml = yaml.safe_load(file)
            return Config(**raw_yaml)
    except Exception as ex:
        raise ConfigurationError(
            f"Failed to load configuration file ({config_path}): {ex}"
        ) from ex


# Singleton instance loaded on import
config = load_config()