"""Building part feature models for Overture Maps buildings theme."""

from pydantic import Field, field_validator

from overture.schema.buildings.common import BaseBuildingProperties
from overture.schema.core.base import OvertureFeature, register_model


class BuildingPartProperties(BaseBuildingProperties):
    """Properties specific to building_part features."""

    # Required for building parts
    building_id: str = Field(..., min_length=1, description="Parent building ID")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v != "building_part":
            raise ValueError("Building part type must be 'building_part'")
        return v


class BuildingPartFeature(OvertureFeature):
    """Building part feature model."""

    properties: BuildingPartProperties = Field(
        ..., description="Building part feature properties"
    )

    @field_validator("geometry")
    @classmethod
    def validate_geometry_type(cls, v):
        """Building parts must have Polygon or MultiPolygon geometry."""
        # Call parent validation first
        super().validate_geometry_structure(v)

        geom_type = v.get("type")
        valid_types = ["Polygon", "MultiPolygon"]
        if geom_type not in valid_types:
            raise ValueError(
                f"Building part geometry must be one of {valid_types}, got {geom_type}"
            )
        return v


# Register Pydantic models when module is imported
register_model("buildings", "building_part", BuildingPartFeature)
