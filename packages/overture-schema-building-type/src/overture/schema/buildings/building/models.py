"""Building feature models for Overture Maps buildings theme."""

from __future__ import annotations

from typing import Annotated, Any, Dict

from pydantic import Field

from overture.schema.buildings.common import BaseBuildingProperties
from overture.schema.core.base import OvertureFeature, register_model
from overture.schema.validation import (
    GeometryTypeConstraint,
    type_literal,
)


class BuildingProperties(BaseBuildingProperties):
    """Properties specific to building features."""

    # Override type with constraint-based validation
    type: type_literal("building") = Field("building", description="Feature type")


class BuildingFeature(OvertureFeature):
    """Building feature model."""

    properties: BuildingProperties = Field(
        ..., description="Building feature properties"
    )
    geometry: Annotated[
        Dict[str, Any], GeometryTypeConstraint(["Polygon", "MultiPolygon"])
    ] = Field(..., description="GeoJSON geometry (Polygon or MultiPolygon)")


# Register Pydantic models when module is imported
register_model("buildings", "building", BuildingFeature)
