from pydantic import BaseModel, Field


class ImageAsset(BaseModel):
    asset_id: str = ""

    prompt: str = ""

    provider: str = ""

    filename: str = ""

    width: int = 0

    height: int = 0

    metadata: dict = Field(default_factory=dict)


class ImageData(BaseModel):
    assets: list[ImageAsset] = Field(default_factory=list)