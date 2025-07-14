"""Building feature models for Overture Maps buildings theme."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from overture.schema.buildings.common import BaseBuildingProperties
from overture.schema.core.base import OvertureFeature, register_model
from overture.schema.core.geometry import Geometry, GeometryTypeConstraint
from overture.schema.validation import (
    type_literal,
)


class BuildingProperties(BaseBuildingProperties):
    """Properties specific to building features."""

    # Override type with constraint-based validation
    type: type_literal("building") = Field("building", description="Feature type")


class Building(OvertureFeature):
    """Building feature model."""

    properties: BuildingProperties = Field(
        ..., description="Building feature properties"
    )
    geometry: Annotated[Geometry, GeometryTypeConstraint("Polygon", "MultiPolygon")] = (
        Field(..., description="Geometry (Polygon or MultiPolygon)")
    )


# Register Pydantic models when module is imported
register_model("buildings", "building", Building)
