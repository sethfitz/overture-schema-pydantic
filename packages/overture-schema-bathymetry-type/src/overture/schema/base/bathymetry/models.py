"""Bathymetry feature models for Overture Maps base theme."""

from typing import Annotated, Any, Dict

from pydantic import Field

from overture.schema.core.base import (
    OvertureFeature,
    OvertureFeatureProperties,
    register_model,
)
from overture.schema.validation import (
    GeometryTypeConstraint,
    theme_literal,
    type_literal,
)


class BathymetryProperties(OvertureFeatureProperties):
    """Properties specific to bathymetry features."""

    # Required properties
    depth: int = Field(..., ge=0, description="Water depth in meters (>= 0)")
    theme: Annotated[str, theme_literal("base")]
    type: Annotated[str, type_literal("bathymetry")]


class BathymetryFeature(OvertureFeature):
    """Bathymetry feature model."""

    properties: BathymetryProperties = Field(
        ..., description="Bathymetry feature properties"
    )
    geometry: Annotated[
        Dict[str, Any], GeometryTypeConstraint(["Polygon", "MultiPolygon"])
    ]


# Register Pydantic models when module is imported
register_model("base", "bathymetry", BathymetryFeature)
