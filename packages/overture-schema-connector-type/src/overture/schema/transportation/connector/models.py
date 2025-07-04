"""Connector feature models for Overture Maps transportation theme."""

from typing import Annotated, Dict, Any, Optional

from pydantic import Field

from overture.schema.validation import (
    theme_literal,
    type_literal,
    GeometryTypeConstraint,
)
from overture.schema.core.base import (
    OvertureFeature,
    OvertureFeatureProperties,
    register_model,
)


class ConnectorProperties(OvertureFeatureProperties):
    """Properties specific to connector features."""

    # Override theme and type with constraint-based validation
    theme: theme_literal("transportation") = Field(
        "transportation", description="Feature theme"
    )
    type: type_literal("connector") = Field("connector", description="Feature type")

    # Connectors are very simple - they mostly just support extension fields

    # Optional level property for z-order
    level: Optional[int] = Field(None, description="Z-order level")


class ConnectorFeature(OvertureFeature):
    """Connector feature model."""

    properties: ConnectorProperties = Field(
        ..., description="Connector feature properties"
    )
    geometry: Annotated[Dict[str, Any], GeometryTypeConstraint(["Point"])] = Field(
        ..., description="GeoJSON geometry (Point)"
    )


# Register Pydantic models when module is imported

register_model("transportation", "connector", ConnectorFeature)
