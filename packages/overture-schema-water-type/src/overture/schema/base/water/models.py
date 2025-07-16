"""Water feature models for Overture Maps base theme."""

from enum import Enum
from typing import Annotated, Any

from pydantic import Field

from overture.schema.core.base import (
    OvertureFeature,
    register_model,
)
from overture.schema.core.common import (
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


class Water(OvertureFeature):
    """Water feature model."""

    # Override theme and type with constraint-based validation
    theme: theme_literal("base") = Field("base", description="Feature theme")
    type: type_literal("water") = Field("water", description="Feature type")

    # Required properties
    subtype: WaterSubtype = Field(..., description="Water subtype")
    class_: WaterClass = Field(..., alias="class", description="Water class")

    # Optional properties
    is_salt: bool | None = Field(None, description="Is it salt water or not")
    is_intermittent: bool | None = Field(
        None, description="Is it intermittent water or not"
    )

    # Complex containers
    names: NamesContainer | None = Field(None, description="Multilingual names")

    # Source tags from OpenStreetMap
    source_tags: dict[str, Any] | None = Field(
        None, description="Source tags from data providers"
    )

    # External identifiers
    wikidata: str | None = Field(None, description="Wikidata identifier")

    geometry: Annotated[
        Geometry,
        GeometryTypeConstraint("Point", "LineString", "Polygon", "MultiPolygon"),
    ] = Field(
        ...,
        description="Geometry (Point, LineString, Polygon, or MultiPolygon)",
    )


# Register Pydantic models when module is imported

register_model("base", "water", Water)
