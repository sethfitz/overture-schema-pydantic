"""Building part feature models for Overture Maps buildings theme."""

from typing import Annotated, Any, Dict

from pydantic import Field

from overture.schema.buildings.common import BaseBuildingProperties
from overture.schema.core.base import OvertureFeature, register_model
from overture.schema.validation import (
    GeometryTypeConstraint,
    type_literal,
)


class BuildingPartProperties(BaseBuildingProperties):
    """Properties specific to building_part features."""

    # Override type with constraint-based validation
    type: type_literal("building_part") = Field(
        "building_part", description="Feature type"
    )

    # Required for building parts
    building_id: str = Field(..., min_length=1, description="Parent building ID")


class BuildingPart(OvertureFeature):
    """Building part feature model."""

    properties: BuildingPartProperties = Field(
        ..., description="Building part feature properties"
    )
    geometry: Annotated[
        Dict[str, Any], GeometryTypeConstraint(["Polygon", "MultiPolygon"])
    ] = Field(..., description="GeoJSON geometry (Polygon or MultiPolygon)")


# Register Pydantic models when module is imported
register_model("buildings", "building_part", BuildingPart)
