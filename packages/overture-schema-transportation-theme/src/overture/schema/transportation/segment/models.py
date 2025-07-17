"""Segment feature models for Overture Maps transportation theme."""

from typing import Annotated, Literal

from pydantic import BaseModel, Field

from overture.schema.core.base import (
    OvertureFeature,
    register_model,
)
from overture.schema.core.common import (
    GeometricRangeScope,
    NamesContainer,
    ScopingConditions,
)
from overture.schema.core.geometry import Geometry, GeometryTypeConstraint
from overture.schema.validation import (
    CompositeUniqueConstraint,
    ConstraintValidatedModel,
    MinItemsConstraint,
    conditional_enum,
    required_if,
    theme_literal,
    type_literal,
)

from ..shared import (
    AccessRestrictionRule as StrictAccessRestrictionRule,
)
from ..shared import (
    ConnectorReference,
    RailClass,
    RoadClass,
    SegmentSubtype,
)
from ..shared import (
    DestinationRule as StrictDestinationRule,
)
from ..shared import (
    LevelRule as StrictLevelRule,
)
from ..shared import (
    ProhibitedTransitionRule as StrictProhibitedTransitionRule,
)
from ..shared import (
    RailFlagRule as StrictRailFlagRule,
)
from ..shared import (
    RoadFlagRule as StrictRoadFlagRule,
)
from ..shared import (
    RouteReference as StrictRouteReference,
)
from ..shared import (
    SpeedLimitRule as StrictSpeedLimitRule,
)
from ..shared import (
    SubclassRule as StrictSubclassRule,
)
from ..shared import (
    SurfaceRule as StrictSurfaceRule,
)
from ..shared import (
    WidthRule as StrictWidthRule,
)


class LevelRule(GeometricRangeScope):
    """Level/elevation rule with scoping."""

    value: int = Field(
        ..., description="Level value (0=ground, positive=above, negative=below)"
    )
    when: ScopingConditions | None = Field(None, description="Scoping conditions")


class RailFlags(BaseModel):
    """Rail-specific boolean flags."""

    is_bridge: bool | None = Field(None, description="Is bridge")
    is_tunnel: bool | None = Field(None, description="Is tunnel")
    is_seasonal: bool | None = Field(None, description="Is seasonal")
    is_construction: bool | None = Field(None, description="Under construction")
    service: Literal["yard", "siding", "spur", "crossover"] | None = Field(
        None, description="Rail service type"
    )


@required_if("subtype", SegmentSubtype.ROAD, ["class_"])
@required_if("subtype", SegmentSubtype.RAIL, ["class_"])
@conditional_enum(
    enum_field="class_",
    condition_field="subtype",
    enum_mapping={
        "road": [e.value for e in RoadClass],
        "rail": [e.value for e in RailClass],
    },
)
class Segment(OvertureFeature, ConstraintValidatedModel):
    """Segment feature model."""

    # Override theme and type with constraint-based validation
    theme: theme_literal("transportation") = Field(
        "transportation", description="Feature theme"
    )
    type: type_literal("segment") = Field("segment", description="Feature type")

    # Required properties
    subtype: SegmentSubtype = Field(..., description="Transportation segment subtype")

    # Optional complex containers
    names: NamesContainer | None = Field(None, description="Multilingual names")

    # Optional basic properties
    level: int | None = Field(None, description="Z-order level")

    # Connector references
    connectors: (
        Annotated[
            list[ConnectorReference], CompositeUniqueConstraint("connector_id", "at")
        ]
        | None
    ) = Field(None, description="Connector references")

    # Route references (strict typed with linear referencing)
    routes: list[StrictRouteReference] | None = Field(
        None, description="Route references"
    )

    # Subtype-specific classification (conditional required)
    class_: str | None = Field(None, alias="class", description="Segment class")
    subclass: str | None = Field(None, description="Segment subclass")

    # Subclass rules
    subclass_rules: list[StrictSubclassRule] | None = Field(
        None, description="Subclass rules"
    )

    # Advanced linear referencing properties (strict typed)
    speed_limits: list[StrictSpeedLimitRule] | None = Field(
        None, description="Speed limit rules"
    )
    access_restrictions: list[StrictAccessRestrictionRule] | None = Field(
        None, description="Access restriction rules"
    )
    road_surface: list[StrictSurfaceRule] | None = Field(
        None, description="Road surface rules"
    )
    level_rules: list[StrictLevelRule] | None = Field(
        None, description="Level/elevation rules"
    )
    width_rules: Annotated[list[StrictWidthRule], MinItemsConstraint(1)] | None = Field(
        None, description="Width rules"
    )

    # Subtype-specific flags (strict typed)
    road_flags: list[StrictRoadFlagRule] | None = Field(
        None, description="Road-specific flags"
    )
    rail_flags: list[StrictRailFlagRule] | None = Field(
        None, description="Rail-specific flags"
    )

    # Advanced transportation features (strict typed)
    destinations: list[StrictDestinationRule] | None = Field(
        None, description="Destination labels"
    )
    prohibited_transitions: list[StrictProhibitedTransitionRule] | None = Field(
        None, description="Turn restrictions"
    )

    geometry: Annotated[Geometry, GeometryTypeConstraint("LineString")] = Field(
        ..., description="Geometry (LineString)"
    )


# Register Pydantic models when module is imported

register_model("transportation", "segment", Segment)
