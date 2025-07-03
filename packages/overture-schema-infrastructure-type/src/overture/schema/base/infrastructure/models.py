"""Infrastructure feature models for Overture Maps base theme."""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator

from overture.schema.base.common import SurfaceMaterial
from overture.schema.core.base import (
    OvertureFeature,
    OvertureFeatureProperties,
    register_model,
)
from overture.schema.core.common import (
    AdvancedSourceItem,
    NamesContainer,
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


class InfrastructureProperties(OvertureFeatureProperties):
    """Properties specific to infrastructure features."""

    # Required properties
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
    sources: Optional[List[AdvancedSourceItem]] = Field(
        None, min_length=1, description="Advanced source information"
    )

    # Source tags from OpenStreetMap
    source_tags: Optional[Dict[str, Any]] = Field(
        None, description="Source tags from data providers"
    )

    @field_validator("theme")
    @classmethod
    def validate_theme(cls, v):
        if v != "base":
            raise ValueError("Infrastructure theme must be 'base'")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v != "infrastructure":
            raise ValueError("Infrastructure type must be 'infrastructure'")
        return v


class InfrastructureFeature(OvertureFeature):
    """Infrastructure feature model."""

    properties: InfrastructureProperties = Field(
        ..., description="Infrastructure feature properties"
    )

    @field_validator("geometry")
    @classmethod
    def validate_geometry_type(cls, v):
        """Infrastructure can have any geometry type."""
        # Call parent validation first
        super().validate_geometry_structure(v)

        geom_type = v.get("type")
        valid_types = [
            "Point",
            "LineString",
            "Polygon",
            "MultiPoint",
            "MultiLineString",
            "MultiPolygon",
        ]
        if geom_type not in valid_types:
            raise ValueError(
                f"Infrastructure geometry must be one of {valid_types}, got {geom_type}"
            )
        return v


# Register Pydantic models when module is imported

register_model("base", "infrastructure", InfrastructureFeature)
