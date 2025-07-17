"""LandCover feature models for Overture Maps base theme."""

from enum import Enum
from typing import Annotated

from pydantic import Field

from overture.schema.core.base import (
    CartographyContainer,
    OvertureFeature,
    register_model,
)
from overture.schema.core.geometry import Geometry, GeometryTypeConstraint
from overture.schema.core.names import (
    NamesContainer,
)
from overture.schema.validation import (
    theme_literal,
    type_literal,
)


class LandCoverSubtype(str, Enum):
    """Subtypes for land_cover features representing Earth's natural surfaces."""

    BARREN = "barren"
    CROP = "crop"
    FOREST = "forest"
    GRASS = "grass"
    MANGROVE = "mangrove"
    MOSS = "moss"
    SHRUB = "shrub"
    SNOW = "snow"
    URBAN = "urban"
    WETLAND = "wetland"


class LandCover(OvertureFeature):
    """LandCover feature model representing Earth's natural surfaces."""

    # Override theme and type with constraint-based validation
    theme: theme_literal("base") = Field("base", description="Feature theme")
    type: type_literal("land_cover") = Field("land_cover", description="Feature type")

    # Required fields
    subtype: LandCoverSubtype = Field(..., description="Type of surface represented")

    # Optional level field (from levelContainer)
    level: int | None = Field(None, description="Z-order level")

    # Optional cartography container
    cartography: CartographyContainer | None = Field(
        None, description="Cartographic display hints"
    )

    # Optional complex containers
    names: NamesContainer | None = Field(None, description="Multilingual names")

    # Geometry constraints - Polygon or MultiPolygon
    geometry: Annotated[Geometry, GeometryTypeConstraint("Polygon", "MultiPolygon")] = (
        Field(..., description="Geometry (Polygon or MultiPolygon)")
    )


# Register Pydantic models when module is imported
register_model("base", "land_cover", LandCover)
