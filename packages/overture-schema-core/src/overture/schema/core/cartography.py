"""Cartography-related models for Overture Maps features."""

from pydantic import BaseModel, Field


class CartographyContainer(BaseModel):
    """Cartographic hints for optimal map display."""

    prominence: int | None = Field(
        None, ge=1, le=100, description="Feature significance/importance"
    )
    min_zoom: int | None = Field(
        None, ge=0, le=23, description="Minimum recommended zoom level"
    )
    max_zoom: int | None = Field(
        None, ge=0, le=23, description="Maximum recommended zoom level"
    )
    sort_key: int | None = Field(None, description="Drawing order (lower = on top)")
