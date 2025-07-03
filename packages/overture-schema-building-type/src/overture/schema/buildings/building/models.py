"""Building feature models for Overture Maps buildings theme."""

from pydantic import Field, field_validator

from overture.schema.buildings.common import BaseBuildingProperties
from overture.schema.core.base import OvertureFeature, register_model


class BuildingProperties(BaseBuildingProperties):
    """Properties specific to building features."""

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v != "building":
            raise ValueError("Building type must be 'building'")
        return v


class BuildingFeature(OvertureFeature):
    """Building feature model."""

    properties: BuildingProperties = Field(
        ..., description="Building feature properties"
    )

    @field_validator("geometry")
    @classmethod
    def validate_geometry_type(cls, v):
        """Buildings must have Polygon or MultiPolygon geometry."""
        # Call parent validation first
        super().validate_geometry_structure(v)

        geom_type = v.get("type")
        valid_types = ["Polygon", "MultiPolygon"]
        if geom_type not in valid_types:
            raise ValueError(
                f"Building geometry must be one of {valid_types}, got {geom_type}"
            )
        return v


# Register Pydantic models when module is imported
register_model("buildings", "building", BuildingFeature)
