"""Connector feature models for Overture Maps transportation theme."""

from typing import Optional

from pydantic import Field, field_validator

from overture.schema.core.base import (
    OvertureFeature,
    OvertureFeatureProperties,
    register_model,
)


class ConnectorProperties(OvertureFeatureProperties):
    """Properties specific to connector features."""

    # Connectors are very simple - they mostly just support extension fields

    # Optional level property for z-order
    level: Optional[int] = Field(None, description="Z-order level")

    @field_validator("theme")
    @classmethod
    def validate_theme(cls, v):
        if v != "transportation":
            raise ValueError("Connector theme must be 'transportation'")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v != "connector":
            raise ValueError("Connector type must be 'connector'")
        return v


class ConnectorFeature(OvertureFeature):
    """Connector feature model."""

    properties: ConnectorProperties = Field(
        ..., description="Connector feature properties"
    )

    @field_validator("geometry")
    @classmethod
    def validate_geometry_type(cls, v):
        """Connectors must have Point geometry."""
        # Call parent validation first
        super().validate_geometry_structure(v)

        geom_type = v.get("type")
        if geom_type != "Point":
            raise ValueError(f"Connector geometry must be Point, got {geom_type}")
        return v


# Register Pydantic models when module is imported

register_model("transportation", "connector", ConnectorFeature)
