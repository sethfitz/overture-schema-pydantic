"""Bathymetry feature models for Overture Maps base theme."""

from pydantic import Field, field_validator

from overture.schema.core.base import (
    OvertureFeature,
    OvertureFeatureProperties,
    register_model,
)


class BathymetryProperties(OvertureFeatureProperties):
    """Properties specific to bathymetry features."""

    # Required properties
    depth: int = Field(..., ge=0, description="Water depth in meters (>= 0)")

    @field_validator("theme")
    @classmethod
    def validate_theme(cls, v):
        if v != "base":
            raise ValueError("Bathymetry theme must be 'base'")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v != "bathymetry":
            raise ValueError("Bathymetry type must be 'bathymetry'")
        return v


class BathymetryFeature(OvertureFeature):
    """Bathymetry feature model."""

    properties: BathymetryProperties = Field(
        ..., description="Bathymetry feature properties"
    )

    @field_validator("geometry")
    @classmethod
    def validate_geometry_type(cls, v):
        """Bathymetry must have Polygon or MultiPolygon geometry."""
        # Call parent validation first
        super().validate_geometry_structure(v)

        geom_type = v.get("type")
        valid_types = ["Polygon", "MultiPolygon"]
        if geom_type not in valid_types:
            raise ValueError(
                f"Bathymetry geometry must be one of {valid_types}, got {geom_type}"
            )
        return v


# Register Pydantic models when module is imported
register_model("base", "bathymetry", BathymetryFeature)
