"""Water feature models for Overture Maps base theme."""

from enum import Enum
from typing import Annotated, Any, Dict, List, Optional

from pydantic import Field

from overture.schema.core.base import (
    OvertureFeature,
    OvertureFeatureProperties,
    register_model,
)
from overture.schema.core.common import (
    AdvancedSourceItem,
    NamesContainer,
)
from overture.schema.core.geometry import Geometry, GeometryTypeConstraint
from overture.schema.validation import (
    theme_literal,
    type_literal,
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

    # Override theme and type with constraint-based validation
    theme: theme_literal("base") = Field("base", description="Feature theme")
    type: type_literal("water") = Field("water", description="Feature type")

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


class Water(OvertureFeature):
    """Water feature model."""

    properties: WaterProperties = Field(..., description="Water feature properties")
    geometry: Annotated[
        Geometry,
        GeometryTypeConstraint("Point", "LineString", "Polygon", "MultiPolygon"),
    ] = Field(
        ...,
        description="Geometry (Point, LineString, Polygon, or MultiPolygon)",
    )


# Register Pydantic models when module is imported

register_model("base", "water", Water)
