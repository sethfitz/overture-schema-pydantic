"""Infrastructure feature models for Overture Maps base theme."""

from enum import Enum
from typing import Annotated, Any, Dict, Optional

from pydantic import Field

from overture.schema.base.common import SurfaceMaterial
from overture.schema.core.base import (
    OvertureFeature,
    register_model,
)
from overture.schema.core.common import (
    NamesContainer,
)
from overture.schema.validation import (
    theme_literal,
    type_literal,
)


class InfrastructureSubtype(str, Enum):
    """Infrastructure subtype classification."""

    AERIALWAY = "aerialway"
    AIRPORT = "airport"
    BARRIER = "barrier"
    BRIDGE = "bridge"
    COMMUNICATION = "communication"
    EMERGENCY = "emergency"
    MANHOLE = "manhole"
    PEDESTRIAN = "pedestrian"
    PIER = "pier"
    POWER = "power"
    RECREATION = "recreation"
    TOWER = "tower"
    TRANSIT = "transit"
    TRANSPORTATION = "transportation"
    UTILITY = "utility"
    WASTE_MANAGEMENT = "waste_management"
    WATER = "water"


class InfrastructureClass(str, Enum):
    """Infrastructure class classification."""

    # Airport
    AIRPORT = "airport"
    AIRSTRIP = "airstrip"
    RUNWAY = "runway"
    TAXIWAY = "taxiway"
    TERMINAL = "terminal"
    HELIPAD = "helipad"

    # Bridge
    BRIDGE = "bridge"
    BRIDGE_SUPPORT = "bridge_support"
    VIADUCT = "viaduct"

    # Power
    GENERATOR = "generator"
    POWER_LINE = "power_line"
    POWER_POLE = "power_pole"
    POWER_TOWER = "power_tower"
    SUBSTATION = "substation"

    # Transportation
    BUS_STATION = "bus_station"
    RAILWAY_STATION = "railway_station"
    FERRY_TERMINAL = "ferry_terminal"

    # Barrier
    FENCE = "fence"
    WALL = "wall"
    GATE = "gate"
    BOLLARD = "bollard"

    # Communication
    COMMUNICATION_TOWER = "communication_tower"
    MOBILE_PHONE_TOWER = "mobile_phone_tower"

    # Add more classes as needed - this is a subset for now


class Infrastructure(OvertureFeature):
    """Infrastructure feature model."""

    # Required properties with constraint-based validation
    theme: Annotated[str, theme_literal("base")] = Field(
        ..., description="Feature theme"
    )
    type: Annotated[str, type_literal("infrastructure")] = Field(
        ..., description="Feature type"
    )
    subtype: InfrastructureSubtype = Field(..., description="Infrastructure subtype")

    # Optional properties
    class_: Optional[InfrastructureClass] = Field(
        None, alias="class", description="Infrastructure class"
    )
    height: Optional[float] = Field(
        None, gt=0, description="Height of the feature in meters"
    )
    surface: Optional[SurfaceMaterial] = Field(None, description="Surface material")

    # Complex containers
    names: Optional[NamesContainer] = Field(None, description="Multilingual names")

    # Source tags from OpenStreetMap
    source_tags: Optional[Dict[str, Any]] = Field(
        None, description="Source tags from data providers"
    )


# Register Pydantic models when module is imported

register_model("base", "infrastructure", Infrastructure)
