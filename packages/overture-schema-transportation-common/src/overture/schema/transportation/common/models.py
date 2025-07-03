"""Common transportation theme structures and enums."""

from enum import Enum
from typing import Annotated, List, Literal, Optional

from pydantic import BaseModel, Field

from overture.schema.core.common import (
    GeometricRangeScopeContainer,
    ScopingConditions,
    Speed,
)
from overture.schema.validation import AtLeastOneOfConstraint


class SegmentSubtype(str, Enum):
    """Transportation segment subtype classification."""

    ROAD = "road"
    RAIL = "rail"
    WATER = "water"


class RoadClass(str, Enum):
    """Road classification enum."""

    MOTORWAY = "motorway"
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    RESIDENTIAL = "residential"
    LIVING_STREET = "living_street"
    TRUNK = "trunk"
    UNCLASSIFIED = "unclassified"
    SERVICE = "service"
    PEDESTRIAN = "pedestrian"
    FOOTWAY = "footway"
    STEPS = "steps"
    PATH = "path"
    TRACK = "track"
    CYCLEWAY = "cycleway"
    BRIDLEWAY = "bridleway"
    UNKNOWN = "unknown"


class RailClass(str, Enum):
    """Rail classification enum."""

    FUNICULAR = "funicular"
    LIGHT_RAIL = "light_rail"
    MONORAIL = "monorail"
    NARROW_GAUGE = "narrow_gauge"
    STANDARD_GAUGE = "standard_gauge"
    SUBWAY = "subway"
    TRAM = "tram"
    UNKNOWN = "unknown"


class ConnectorReference(BaseModel):
    """Reference to a connector with position information."""

    connector_id: str = Field(..., description="Connector identifier")
    at: float = Field(
        ..., ge=0.0, le=1.0, description="Position along segment (0.0-1.0)"
    )


class RouteReference(str):
    """Reference to a route."""

    pass


# Advanced Transportation Properties


class SpeedLimitRule(
    Annotated[
        GeometricRangeScopeContainer, AtLeastOneOfConstraint("min_speed", "max_speed")
    ]
):
    """Speed limit rule with scoping."""

    min_speed: Optional[Speed] = Field(None, description="Minimum speed")
    max_speed: Optional[Speed] = Field(None, description="Maximum speed")
    is_max_speed_variable: bool = Field(False, description="Variable max speed")
    when: Optional[ScopingConditions] = Field(None, description="Scoping conditions")


class AccessRestriction(GeometricRangeScopeContainer):
    """Access restriction rule with scoping."""

    access_type: Literal["allowed", "denied", "designated"] = Field(
        ..., description="Access restriction type"
    )
    when: Optional[ScopingConditions] = Field(None, description="Scoping conditions")


class SurfaceMaterial(str, Enum):
    """Surface material enum for road segments."""

    ASPHALT = "asphalt"
    COBBLESTONE = "cobblestone"
    COMPACTED = "compacted"
    CONCRETE = "concrete"
    CONCRETE_PLATES = "concrete_plates"
    DIRT = "dirt"
    EARTH = "earth"
    FINE_GRAVEL = "fine_gravel"
    GRASS = "grass"
    GRAVEL = "gravel"
    GROUND = "ground"
    PAVED = "paved"
    PAVING_STONES = "paving_stones"
    PEBBLESTONE = "pebblestone"
    RECREATION_GRASS = "recreation_grass"
    RECREATION_PAVED = "recreation_paved"
    RECREATION_SAND = "recreation_sand"
    RUBBER = "rubber"
    SAND = "sand"
    STONE = "stone"
    UNKNOWN = "unknown"
    UNPAVED = "unpaved"
    WOOD = "wood"


class SurfaceRule(GeometricRangeScopeContainer):
    """Road surface rule with scoping."""

    value: SurfaceMaterial = Field(..., description="Surface type")
    when: Optional[ScopingConditions] = Field(None, description="Scoping conditions")


class WidthRule(GeometricRangeScopeContainer):
    """Width rule with scoping."""

    value: float = Field(..., description="Width in meters")
    when: Optional[ScopingConditions] = Field(None, description="Scoping conditions")


class RoadFlag(str, Enum):
    """Valid road flags."""

    IS_ABANDONED = "is_abandoned"
    IS_COVERED = "is_covered"
    IS_INDOOR = "is_indoor"
    IS_LINK = "is_link"
    IS_TUNNEL = "is_tunnel"


class RoadFlagsRule(GeometricRangeScopeContainer):
    """Road flags rule with scoping."""

    values: List[RoadFlag] = Field(..., min_length=1, description="Road flag values")
    when: Optional[ScopingConditions] = Field(None, description="Scoping conditions")


class TurnRestriction(BaseModel):
    """Turn restriction with sequence of connectors."""

    sequence: List[str] = Field(
        ..., min_length=1, description="Sequence of connector IDs"
    )
    when: Optional[ScopingConditions] = Field(None, description="Scoping conditions")


class DestinationLabel(BaseModel):
    """Destination label with symbols and text."""

    text: str = Field(..., description="Destination text")
    symbol: Optional[str] = Field(None, description="Destination symbol")
    language: Optional[str] = Field(None, description="Language code")
