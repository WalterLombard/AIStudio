from pydantic import BaseModel, Field


class VisualAsset(BaseModel):
    asset_id: str = ""

    prompt: str = ""

    asset_type: str = ""

    provider: str = ""

    filename: str = ""

    width: int = 0

    height: int = 0

    duration: float = 0.0

    metadata: dict = Field(default_factory=dict)


class VisualData(BaseModel):
    assets: list[VisualAsset] = Field(default_factory=list)