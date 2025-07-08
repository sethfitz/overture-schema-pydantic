"""Segment feature models for Overture Maps transportation theme."""

from typing import Annotated, Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


from overture.schema.core.base import (
    OvertureFeature,
    OvertureFeatureProperties,
    register_model,
)
from overture.schema.core.common import (
    AdvancedSourceItem,
    GeometricRangeScope,
    NamesContainer,
    ScopingConditions,
)
from overture.schema.transportation.common import (
    ConnectorReference,
    RailClass,
    RoadClass,
    SegmentSubtype,
)
from overture.schema.transportation.rules import (
    AccessRestrictionRule as StrictAccessRestrictionRule,
)
from overture.schema.transportation.rules import (
    DestinationRule as StrictDestinationRule,
)
from overture.schema.transportation.rules import (
    LevelRule as StrictLevelRule,
)
from overture.schema.transportation.rules import (
    ProhibitedTransitionRule as StrictProhibitedTransitionRule,
)
from overture.schema.transportation.rules import (
    RailFlagRule as StrictRailFlagRule,
)
from overture.schema.transportation.rules import (
    RoadFlagRule as StrictRoadFlagRule,
)
from overture.schema.transportation.rules import (
    RouteReference as StrictRouteReference,
)

# Import new strict rule types from transportation rules
from overture.schema.transportation.rules import (
    SpeedLimitRule as StrictSpeedLimitRule,
)
from overture.schema.transportation.rules import (
    SubclassRule as StrictSubclassRule,
)
from overture.schema.transportation.rules import (
    SurfaceRule as StrictSurfaceRule,
)
from overture.schema.transportation.rules import (
    WidthRule as StrictWidthRule,
)
from overture.schema.validation import (
    CompositeUniqueConstraint,
    ConstraintValidatedModel,
    GeometryTypeConstraint,
    MinItemsConstraint,
    conditional_enum,
    required_if,
    theme_literal,
    type_literal,
)


class LevelRule(GeometricRangeScope):
    """Level/elevation rule with scoping."""

    value: int = Field(
        ..., description="Level value (0=ground, positive=above, negative=below)"
    )
    when: Optional[ScopingConditions] = Field(None, description="Scoping conditions")


class RailFlags(BaseModel):
    """Rail-specific boolean flags."""

    is_bridge: Optional[bool] = Field(None, description="Is bridge")
    is_tunnel: Optional[bool] = Field(None, description="Is tunnel")
    is_seasonal: Optional[bool] = Field(None, description="Is seasonal")
    is_construction: Optional[bool] = Field(None, description="Under construction")
    service: Optional[Literal["yard", "siding", "spur", "crossover"]] = Field(
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
class SegmentProperties(ConstraintValidatedModel, OvertureFeatureProperties):
    """Properties specific to segment features."""

    # Override theme and type with constraint-based validation
    theme: theme_literal("transportation") = Field(
        "transportation", description="Feature theme"
    )
    type: type_literal("segment") = Field("segment", description="Feature type")

    # Required properties
    subtype: SegmentSubtype = Field(..., description="Transportation segment subtype")

    # Optional complex containers
    names: Optional[NamesContainer] = Field(None, description="Multilingual names")

    # Override sources to use advanced source items
    sources: Optional[Annotated[List[AdvancedSourceItem], MinItemsConstraint(1)]] = (
        Field(None, description="Advanced source information")
    )

    # Optional basic properties
    level: Optional[int] = Field(None, description="Z-order level")

    # Connector references
    connectors: Optional[
        Annotated[
            List[ConnectorReference], CompositeUniqueConstraint("connector_id", "at")
        ]
    ] = Field(None, description="Connector references")

    # Route references (strict typed with linear referencing)
    routes: Optional[List[StrictRouteReference]] = Field(
        None, description="Route references"
    )

    # Subtype-specific classification (conditional required)
    class_: Optional[str] = Field(None, alias="class", description="Segment class")
    subclass: Optional[str] = Field(None, description="Segment subclass")

    # Subclass rules
    subclass_rules: Optional[List[StrictSubclassRule]] = Field(
        None, description="Subclass rules"
    )

    # Advanced linear referencing properties (strict typed)
    speed_limits: Optional[List[StrictSpeedLimitRule]] = Field(
        None, description="Speed limit rules"
    )
    access_restrictions: Optional[List[StrictAccessRestrictionRule]] = Field(
        None, description="Access restriction rules"
    )
    road_surface: Optional[List[StrictSurfaceRule]] = Field(
        None, description="Road surface rules"
    )
    level_rules: Optional[List[StrictLevelRule]] = Field(
        None, description="Level/elevation rules"
    )
    width_rules: Optional[Annotated[List[StrictWidthRule], MinItemsConstraint(1)]] = (
        Field(None, description="Width rules")
    )

    # Subtype-specific flags (strict typed)
    road_flags: Optional[List[StrictRoadFlagRule]] = Field(
        None, description="Road-specific flags"
    )
    rail_flags: Optional[List[StrictRailFlagRule]] = Field(
        None, description="Rail-specific flags"
    )

    # Advanced transportation features (strict typed)
    destinations: Optional[List[StrictDestinationRule]] = Field(
        None, description="Destination labels"
    )
    prohibited_transitions: Optional[List[StrictProhibitedTransitionRule]] = Field(
        None, description="Turn restrictions"
    )


class SegmentFeature(OvertureFeature):
    """Segment feature model."""

    properties: SegmentProperties = Field(..., description="Segment feature properties")
    geometry: Annotated[Dict[str, Any], GeometryTypeConstraint(["LineString"])] = Field(
        ..., description="GeoJSON geometry (LineString)"
    )


# Register Pydantic models when module is imported

register_model("transportation", "segment", SegmentFeature)
