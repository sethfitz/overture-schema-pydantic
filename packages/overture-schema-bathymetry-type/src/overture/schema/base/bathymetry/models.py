"""Bathymetry feature models for Overture Maps base theme."""

from typing import Annotated

from pydantic import Field

from overture.schema.core.base import (
    OvertureFeature,
    OvertureFeatureProperties,
    register_model,
)
from overture.schema.core.geometry import Geometry, GeometryTypeConstraint
from overture.schema.validation import (
    theme_literal,
    type_literal,
)


class BathymetryProperties(OvertureFeatureProperties):
    """Properties specific to bathymetry features."""

    # Required properties
    depth: int = Field(..., ge=0, description="Water depth in meters (>= 0)")
    theme: Annotated[str, theme_literal("base")]
    type: Annotated[str, type_literal("bathymetry")]


class Bathymetry(OvertureFeature):
    """Bathymetry feature model."""

    properties: BathymetryProperties = Field(
        ..., description="Bathymetry feature properties"
    )
    geometry: Annotated[Geometry, GeometryTypeConstraint("Polygon", "MultiPolygon")] = (
        Field(..., description="Geometry (Polygon or MultiPolygon)")
    )


# Register Pydantic models when module is imported
register_model("base", "bathymetry", Bathymetry)
