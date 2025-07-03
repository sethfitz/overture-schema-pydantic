"""Transportation rule models using mix-in architecture."""

from enum import Enum
from typing import Annotated, List, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator

from overture.schema.validation import (
    CompositeUniqueConstraint,
    UniqueItemsConstraint,
)

from overture.schema.core.common import (
    GeometricRangeScopeContainer,
    HeadingScopeContainer,
    PurposeOfUseScopeContainer,
    RecognizedStatusScopeContainer,
    Speed,
    TemporalScopeContainer,
    TravelModeScopeContainer,
    VehicleScopeContainer,
)


class AccessLevel(str, Enum):
    """Access level enumeration."""

    YES = "yes"
    NO = "no"
    DESIGNATED = "designated"
    DESTINATION = "destination"
    PRIVATE = "private"
    PERMISSIVE = "permissive"
    CUSTOMERS = "customers"
    DELIVERY = "delivery"


class DestinationLabelType(str, Enum):
    """Destination label type classification."""

    UNKNOWN = "unknown"
    STREET = "street"
    ROUTE_REF = "route_ref"
    TOWARD_ROUTE_REF = "toward_route_ref"


class TurnDirection(str, Enum):
    """Turn direction for prohibited transitions."""

    STRAIGHT = "straight"
    SLIGHT_LEFT = "slight_left"
    LEFT = "left"
    SHARP_LEFT = "sharp_left"
    SLIGHT_RIGHT = "slight_right"
    RIGHT = "right"
    SHARP_RIGHT = "sharp_right"
    REVERSE = "reverse"


class RoadFlagType(str, Enum):
    """Road-specific flag types."""

    IS_BRIDGE = "is_bridge"
    IS_LINK = "is_link"  # Deprecated - will be removed in favor of link subclass
    IS_TUNNEL = "is_tunnel"
    IS_UNDER_CONSTRUCTION = "is_under_construction"
    IS_ABANDONED = "is_abandoned"
    IS_COVERED = "is_covered"
    IS_INDOOR = "is_indoor"


class RailFlagType(str, Enum):
    """Rail-specific flag types."""

    IS_BRIDGE = "is_bridge"
    IS_TUNNEL = "is_tunnel"  # Also used for subway class (though subways occasionally above-ground)
    IS_UNDER_CONSTRUCTION = "is_under_construction"
    IS_ABANDONED = "is_abandoned"
    IS_COVERED = "is_covered"
    IS_PASSENGER = "is_passenger"
    IS_FREIGHT = "is_freight"
    IS_DISUSED = "is_disused"


class RoadSurface(str, Enum):
    """Road surface material types."""

    UNKNOWN = "unknown"
    PAVED = "paved"
    UNPAVED = "unpaved"
    GRAVEL = "gravel"
    DIRT = "dirt"
    PAVING_STONES = "paving_stones"
    METAL = "metal"


# Scoping condition models for when clauses
class SpeedLimitWhenClause(
    TemporalScopeContainer,
    HeadingScopeContainer,
    PurposeOfUseScopeContainer,
    RecognizedStatusScopeContainer,
    TravelModeScopeContainer,
    VehicleScopeContainer,
):
    """When clause for speed limit rules."""

    pass


class AccessRestrictionWhenClause(
    TemporalScopeContainer,
    HeadingScopeContainer,
    PurposeOfUseScopeContainer,
    RecognizedStatusScopeContainer,
    TravelModeScopeContainer,
    VehicleScopeContainer,
):
    """When clause for access restriction rules."""

    pass


class ProhibitedTransitionWhenClause(
    HeadingScopeContainer,
    TemporalScopeContainer,
    PurposeOfUseScopeContainer,
    RecognizedStatusScopeContainer,
    TravelModeScopeContainer,
    VehicleScopeContainer,
):
    """When clause for prohibited transition rules."""

    pass


class DestinationWhenClause(HeadingScopeContainer):
    """When clause for destination rules."""

    pass


# Core rule models using mix-in composition
class SpeedLimitRule(GeometricRangeScopeContainer):
    """Speed limit rule with scoping via when clause."""

    max_speed: Optional[Speed] = Field(None, description="Maximum speed limit")
    min_speed: Optional[Speed] = Field(None, description="Minimum speed limit")
    is_max_speed_variable: Optional[bool] = Field(
        None, description="Whether maximum speed is variable"
    )
    when: Optional[SpeedLimitWhenClause] = Field(None, description="Scoping conditions")

    @model_validator(mode="after")
    def validate_speed_required(self):
        """At least one of max_speed or min_speed is required."""
        if not self.max_speed and not self.min_speed:
            raise ValueError("Either max_speed or min_speed is required")
        return self


class AccessRestrictionRule(GeometricRangeScopeContainer):
    """Access restriction rule with scoping via when clause."""

    access_type: Literal["allowed", "denied", "designated"] = Field(
        ..., description="Access type"
    )
    when: Optional[AccessRestrictionWhenClause] = Field(
        None, description="Scoping conditions"
    )


class DestinationLabel(BaseModel):
    """Destination label with type classification."""

    value: str = Field(..., min_length=1, description="Label text")
    type: DestinationLabelType = Field(..., description="Label type")


class DestinationSignSymbol(str, Enum):
    """Valid destination sign symbols."""

    MOTORWAY = "motorway"
    AIRPORT = "airport"
    HOSPITAL = "hospital"
    CENTER = "center"
    INDUSTRIAL = "industrial"
    PARKING = "parking"


class DestinationRule(BaseModel):
    """Destination signage rule with scoping via when clause."""

    from_connector_id: str = Field(..., description="Source connector identifier")
    to_connector_id: str = Field(..., description="Target connector identifier")
    to_segment_id: str = Field(..., description="Target segment identifier")
    final_heading: Literal["forward", "backward"] = Field(
        ..., description="Final direction on target segment"
    )
    labels: Annotated[
        List[DestinationLabel], CompositeUniqueConstraint("value", "type")
    ] = Field(..., min_length=1, description="Destination labels")
    symbols: Optional[
        Annotated[List[DestinationSignSymbol], UniqueItemsConstraint()]
    ] = Field(None, description="Route symbols")
    when: Optional[DestinationWhenClause] = Field(
        None, description="Scoping conditions"
    )


class ProhibitedTransitionSequence(BaseModel):
    """Sequence entry with connector and segment identifiers."""

    connector_id: str = Field(..., description="Connector identifier")
    segment_id: str = Field(..., description="Segment identifier")


class ProhibitedTransitionRule(GeometricRangeScopeContainer):
    """Prohibited transition (turn restriction) rule."""

    sequence: Annotated[
        List[ProhibitedTransitionSequence],
        CompositeUniqueConstraint("connector_id", "segment_id"),
    ] = Field(
        ...,
        min_length=1,
        description="Sequence of connectors defining the prohibited path",
    )
    final_heading: Literal["forward", "backward"] = Field(
        ..., description="Required final heading"
    )
    when: Optional[ProhibitedTransitionWhenClause] = Field(
        None, description="Scoping conditions"
    )


class RoadFlagRule(GeometricRangeScopeContainer):
    """Road-specific flag rule with geometric scoping only."""

    values: Annotated[List[RoadFlagType], UniqueItemsConstraint()] = Field(
        ..., min_length=1, description="Road flag values"
    )


class RailFlagRule(GeometricRangeScopeContainer):
    """Rail-specific flag rule with geometric scoping only."""

    values: Annotated[List[RailFlagType], UniqueItemsConstraint()] = Field(
        ..., min_length=1, description="Rail flag values"
    )


class WidthRule(GeometricRangeScopeContainer):
    """Width rule with linear referencing."""

    value: Union[int, float] = Field(..., description="Width value")


class SurfaceRule(GeometricRangeScopeContainer):
    """Surface material rule with linear referencing."""

    value: RoadSurface = Field(..., description="Surface material")


class LevelRule(GeometricRangeScopeContainer):
    """Level/elevation rule with linear referencing."""

    value: int = Field(..., description="Level/elevation value")


class SubclassRule(GeometricRangeScopeContainer):
    """Subclass rule with linear referencing."""

    value: str = Field(..., description="Subclass value")


class RouteReference(GeometricRangeScopeContainer):
    """Route reference with linear referencing support."""

    name: Optional[str] = Field(None, description="Route name")
    network: Optional[str] = Field(None, description="Route network")
    ref: Optional[str] = Field(None, description="Route reference number")
    symbol: Optional[str] = Field(None, description="Route symbol URL")
    wikidata: Optional[str] = Field(None, description="Wikidata identifier")
