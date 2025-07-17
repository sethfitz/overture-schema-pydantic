"""Connector feature models for Overture Maps transportation theme."""

from typing import Annotated

from pydantic import Field

from overture.schema.core.base import (
    OvertureFeature,
    register_model,
)
from overture.schema.core.geometry import Geometry, GeometryTypeConstraint
from overture.schema.validation import (
    theme_literal,
    type_literal,
)


class Connector(OvertureFeature):
    """Connector feature model."""

    # Override theme and type with constraint-based validation
    theme: theme_literal("transportation") = Field(
        "transportation", description="Feature theme"
    )
    type: type_literal("connector") = Field("connector", description="Feature type")

    geometry: Annotated[Geometry, GeometryTypeConstraint("Point")] = Field(
        ..., description="Geometry (Point)"
    )


# Register Pydantic models when module is imported

register_model("transportation", "connector", Connector)
