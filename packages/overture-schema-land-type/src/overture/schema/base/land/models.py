"""Land feature models for Overture Maps base theme."""

from enum import Enum
from typing import Annotated, Any, Dict, List, Optional

from pydantic import Field

from overture.schema.base.common import SurfaceMaterial
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


class LandSubtype(str, Enum):
    """Land subtype classification."""

    CRATER = "crater"
    DESERT = "desert"
    FOREST = "forest"
    GLACIER = "glacier"
    GRASS = "grass"
    LAND = "land"
    PHYSICAL = "physical"
    REEF = "reef"
    ROCK = "rock"
    SAND = "sand"
    SHRUB = "shrub"
    TREE = "tree"
    WETLAND = "wetland"


class LandClass(str, Enum):
    """Land class classification."""

    ARCHIPELAGO = "archipelago"
    BARE_ROCK = "bare_rock"
    BEACH = "beach"
    CAVE_ENTRANCE = "cave_entrance"
    CLIFF = "cliff"
    DESERT = "desert"
    DUNE = "dune"
    FELL = "fell"
    FOREST = "forest"
    GLACIER = "glacier"
    GRASS = "grass"
    GRASSLAND = "grassland"
    HEATH = "heath"
    HILL = "hill"
    ISLAND = "island"
    ISLET = "islet"
    LAND = "land"
    MEADOW = "meadow"
    METEOR_CRATER = "meteor_crater"
    MOUNTAIN_RANGE = "mountain_range"
    PEAK = "peak"
    PENINSULA = "peninsula"
    PLATEAU = "plateau"
    REEF = "reef"
    RIDGE = "ridge"
    ROCK = "rock"
    SADDLE = "saddle"
    SAND = "sand"
    SCREE = "scree"
    SCRUB = "scrub"
    SHINGLE = "shingle"
    SHRUB = "shrub"
    SHRUBBERY = "shrubbery"
    STONE = "stone"
    TREE = "tree"
    TREE_ROW = "tree_row"
    TUNDRA = "tundra"
    VALLEY = "valley"
    VOLCANIC_CALDERA_RIM = "volcanic_caldera_rim"
    VOLCANO = "volcano"
    WETLAND = "wetland"
    WOOD = "wood"


class LandProperties(OvertureFeatureProperties):
    """Properties specific to land features."""

    # Required properties
    theme: Annotated[str, theme_literal("base")] = "base"
    type: Annotated[str, type_literal("land")] = "land"
    subtype: LandSubtype = Field(..., description="Land subtype")
    class_: LandClass = Field(..., alias="class", description="Land class")

    # Optional properties
    elevation: Optional[int] = Field(
        None, le=9000, description="Elevation above sea level in meters"
    )
    surface: Optional[SurfaceMaterial] = Field(None, description="Surface material")

    # Complex containers
    names: Optional[NamesContainer] = Field(None, description="Multilingual names")
    sources: Optional[List[AdvancedSourceItem]] = Field(
        None, min_length=1, description="Advanced source information"
    )

    # Source tags from OpenStreetMap
    source_tags: Optional[Dict[str, Any]] = Field(
        None, description="Source tags from data providers"
    )


class Land(OvertureFeature):
    """Land feature model."""

    properties: LandProperties = Field(..., description="Land feature properties")
    geometry: Annotated[
        Geometry,
        GeometryTypeConstraint("Point", "LineString", "Polygon", "MultiPolygon"),
    ] = Field(..., description="Geometry (Point, LineString, Polygon, or MultiPolygon)")


# Register Pydantic models when module is imported

register_model("base", "land", Land)
