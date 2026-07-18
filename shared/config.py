from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel


# ==========================================================
# Configuration File Location
# ==========================================================

ROOT = Path(__file__).resolve().parent.parent

CONFIG_FILE = ROOT / "config" / "config.yaml"


# ==========================================================
# Application
# ==========================================================

class ApplicationConfig(BaseModel):

    name: str

    version: str


# ==========================================================
# Project Paths
# ==========================================================

class PathsConfig(BaseModel):

    projects: str

    logs: str

    cache: str

    prompts: str

    schemas: str

    assets: str

    templates: str


# ==========================================================
# LLM Configuration
# ==========================================================

class LLMConfig(BaseModel):

    provider: str

    model: str

    endpoint: str

    temperature: float

    num_predict: int


# ==========================================================
# Image Model Configuration
# ==========================================================

class ImageConfig(BaseModel):

    provider: str

    model: str


# ==========================================================
# Video Model Configuration
# ==========================================================

class VideoConfig(BaseModel):

    provider: str

    model: str


# ==========================================================
# Models
# ==========================================================

class ModelsConfig(BaseModel):

    llm: LLMConfig

    image: ImageConfig

    video: VideoConfig


# ==========================================================
# Logging
# ==========================================================

class LoggingConfig(BaseModel):

    level: Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
    ]


# ==========================================================
# Root Configuration
# ==========================================================

class Config(BaseModel):

    application: ApplicationConfig

    paths: PathsConfig

    models: ModelsConfig

    logging: LoggingConfig


# ==========================================================
# Load Configuration
# ==========================================================

with open(CONFIG_FILE, "r", encoding="utf-8") as file:

    config = Config(
        **yaml.safe_load(file)
    )