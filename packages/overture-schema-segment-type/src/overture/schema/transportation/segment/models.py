"""Segment feature models for Overture Maps transportation theme."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

from overture.schema.core.base import (
    OvertureFeature,
    OvertureFeatureProperties,
    register_model,
)
from overture.schema.core.common import (
    AdvancedSourceItem,
    GeometricRangeScopeContainer,
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


class LevelRule(GeometricRangeScopeContainer):
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


class SegmentProperties(OvertureFeatureProperties):
    """Properties specific to segment features."""

    # Required properties
    subtype: SegmentSubtype = Field(..., description="Transportation segment subtype")

    # Optional complex containers
    names: Optional[NamesContainer] = Field(None, description="Multilingual names")

    # Override sources to use advanced source items
    sources: Optional[List[AdvancedSourceItem]] = Field(
        None, min_length=1, description="Advanced source information"
    )

    # Optional basic properties
    level: Optional[int] = Field(None, description="Z-order level")

    # Connector references
    connectors: Optional[List[ConnectorReference]] = Field(
        None, description="Connector references"
    )

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
    width_rules: Optional[List[StrictWidthRule]] = Field(
        None, min_length=1, description="Width rules"
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

    @field_validator("theme")
    @classmethod
    def validate_theme(cls, v):
        if v != "transportation":
            raise ValueError("Segment theme must be 'transportation'")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v != "segment":
            raise ValueError("Segment type must be 'segment'")
        return v

    @field_validator("class_")
    @classmethod
    def validate_class_with_subtype(cls, v, info):
        """Class is required for segments and must match subtype."""
        if hasattr(info, "data"):
            subtype = info.data.get("subtype")
            if subtype in [SegmentSubtype.ROAD, SegmentSubtype.RAIL]:
                if v is None:
                    raise ValueError("Road and rail segments must have class property")

                # Validate against appropriate enum
                if subtype == SegmentSubtype.ROAD:
                    valid_classes = [e.value for e in RoadClass]
                    if v not in valid_classes:
                        raise ValueError(f"Invalid road class: {v}")
                elif subtype == SegmentSubtype.RAIL:
                    valid_classes = [e.value for e in RailClass]
                    if v not in valid_classes:
                        raise ValueError(f"Invalid rail class: {v}")
        return v

    @field_validator("road_flags")
    @classmethod
    def validate_road_flags_with_subtype(cls, v, info):
        """Road flags can only be used with road subtype."""
        if v is not None and hasattr(info, "data"):
            subtype = info.data.get("subtype")
            if subtype != SegmentSubtype.ROAD:
                raise ValueError(
                    f"road_flags property not allowed for subtype '{subtype}', only for 'road'"
                )
        return v

    @field_validator("rail_flags")
    @classmethod
    def validate_rail_flags_with_subtype(cls, v, info):
        """Rail flags can only be used with rail subtype."""
        if v is not None and hasattr(info, "data"):
            subtype = info.data.get("subtype")
            if subtype != SegmentSubtype.RAIL:
                raise ValueError(
                    f"rail_flags property not allowed for subtype '{subtype}', only for 'rail'"
                )
        return v

    @field_validator("connectors")
    @classmethod
    def validate_connectors_unique(cls, v):
        """Connectors must not have duplicates."""
        if v is not None:
            # Check for duplicate connector references
            seen = set()
            for i, connector in enumerate(v):
                # Create a unique key from connector_id and at position
                key = (connector.connector_id, connector.at)
                if key in seen:
                    raise ValueError(
                        f"Duplicate connector reference found: connector_id='{connector.connector_id}', at={connector.at}"
                    )
                seen.add(key)
        return v


class SegmentFeature(OvertureFeature):
    """Segment feature model."""

    properties: SegmentProperties = Field(..., description="Segment feature properties")

    @field_validator("geometry")
    @classmethod
    def validate_geometry_type(cls, v):
        """Segments must have LineString geometry."""
        # Call parent validation first
        super().validate_geometry_structure(v)

        geom_type = v.get("type")
        if geom_type != "LineString":
            raise ValueError(f"Segment geometry must be LineString, got {geom_type}")
        return v


# Register Pydantic models when module is imported

register_model("transportation", "segment", SegmentFeature)
