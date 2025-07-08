"""Connector feature models for Overture Maps transportation theme."""

from typing import Annotated, Any, Dict, Optional

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


class ConnectorProperties(OvertureFeatureProperties):
    """Properties specific to connector features."""

    # Override theme and type with constraint-based validation
    theme: theme_literal("transportation") = Field(
        "transportation", description="Feature theme"
    )
    type: type_literal("connector") = Field("connector", description="Feature type")


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
