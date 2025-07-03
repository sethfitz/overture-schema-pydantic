"""Water feature models for Overture Maps base theme."""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator

from overture.schema.core.base import (
    OvertureFeature,
    OvertureFeatureProperties,
    register_model,
)
from overture.schema.core.common import (
    AdvancedSourceItem,
    NamesContainer,
)


class WaterSubtype(str, Enum):
    """Water subtype classification."""

    CANAL = "canal"
    HUMAN_MADE = "human_made"
    LAKE = "lake"
    OCEAN = "ocean"
    PHYSICAL = "physical"
    POND = "pond"
    RESERVOIR = "reservoir"
    RIVER = "river"
    SPRING = "spring"
    STREAM = "stream"
    WASTEWATER = "wastewater"
    WATER = "water"


class WaterClass(str, Enum):
    """Water class classification."""

    BASIN = "basin"
    BAY = "bay"
    BLOWHOLE = "blowhole"
    CANAL = "canal"
    CAPE = "cape"
    DITCH = "ditch"
    DOCK = "dock"
    DRAIN = "drain"
    FAIRWAY = "fairway"
    FISH_PASS = "fish_pass"
    FISHPOND = "fishpond"
    GEYSER = "geyser"
    HOT_SPRING = "hot_spring"
    LAGOON = "lagoon"
    LAKE = "lake"
    MOAT = "moat"
    OCEAN = "ocean"
    OXBOW = "oxbow"
    POND = "pond"
    REFLECTING_POOL = "reflecting_pool"
    RESERVOIR = "reservoir"
    RIVER = "river"
    SALT_POND = "salt_pond"
    SEA = "sea"
    SEWAGE = "sewage"
    SHOAL = "shoal"
    SPRING = "spring"
    STRAIT = "strait"
    STREAM = "stream"
    SWIMMING_POOL = "swimming_pool"
    TIDAL_CHANNEL = "tidal_channel"
    WASTEWATER = "wastewater"
    WATER = "water"
    WATER_STORAGE = "water_storage"
    WATERFALL = "waterfall"


class WaterProperties(OvertureFeatureProperties):
    """Properties specific to water features."""

    # Required properties
    subtype: WaterSubtype = Field(..., description="Water subtype")
    class_: WaterClass = Field(..., alias="class", description="Water class")

    # Optional properties
    is_salt: Optional[bool] = Field(None, description="Is it salt water or not")
    is_intermittent: Optional[bool] = Field(
        None, description="Is it intermittent water or not"
    )

    # Complex containers
    names: Optional[NamesContainer] = Field(None, description="Multilingual names")
    sources: Optional[List[AdvancedSourceItem]] = Field(
        None, min_length=1, description="Advanced source information"
    )

    # Source tags from OpenStreetMap
    source_tags: Optional[Dict[str, Any]] = Field(
        None, description="Source tags from data providers"
    )

    # External identifiers
    wikidata: Optional[str] = Field(None, description="Wikidata identifier")

    @field_validator("theme")
    @classmethod
    def validate_theme(cls, v):
        if v != "base":
            raise ValueError("Water theme must be 'base'")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v != "water":
            raise ValueError("Water type must be 'water'")
        return v


class WaterFeature(OvertureFeature):
    """Water feature model."""

    properties: WaterProperties = Field(..., description="Water feature properties")

    @field_validator("geometry")
    @classmethod
    def validate_geometry_type(cls, v):
        """Water supports Point, LineString, Polygon, MultiPolygon."""
        # Call parent validation first
        super().validate_geometry_structure(v)

        geom_type = v.get("type")
        valid_types = ["Point", "LineString", "Polygon", "MultiPolygon"]
        if geom_type not in valid_types:
            raise ValueError(
                f"Water geometry must be one of {valid_types}, got {geom_type}"
            )
        return v


# Register Pydantic models when module is imported

register_model("base", "water", WaterFeature)
