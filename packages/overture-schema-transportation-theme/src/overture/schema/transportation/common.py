"""Re-export common transportation structures from the transportation-common package."""

# Re-export everything from the common package for backward compatibility
from overture.schema.transportation.common import (
    AccessRestriction,
    ConnectorReference,
    DestinationLabel,
    RailClass,
    RoadClass,
    RoadFlag,
    RoadFlagsRule,
    RouteReference,
    SegmentSubtype,
    SpeedLimitRule,
    SurfaceMaterial,
    SurfaceRule,
    TurnRestriction,
    WidthRule,
)

__all__ = [
    "SegmentSubtype",
    "RoadClass",
    "RailClass",
    "ConnectorReference",
    "RouteReference",
    "SpeedLimitRule",
    "AccessRestriction",
    "SurfaceMaterial",
    "SurfaceRule",
    "WidthRule",
    "RoadFlag",
    "RoadFlagsRule",
    "TurnRestriction",
    "DestinationLabel",
]
