"""Common structures and enums shared across building types."""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from overture.schema.core.base import OvertureFeatureProperties
from overture.schema.core.common import (
    AddressContainer,
    AdvancedSourceItem,
    NamesContainer,
)
from overture.schema.validation import HexColor, theme_literal


class BuildingSubtype(str, Enum):
    """Building subtype classification."""

    AGRICULTURAL = "agricultural"
    CIVIC = "civic"
    COMMERCIAL = "commercial"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    INDUSTRIAL = "industrial"
    MEDICAL = "medical"
    MILITARY = "military"
    OUTBUILDING = "outbuilding"
    RELIGIOUS = "religious"
    RESIDENTIAL = "residential"
    SERVICE = "service"
    TRANSPORTATION = "transportation"


class BuildingClass(str, Enum):
    """Building class classification (84 total values)."""

    AGRICULTURAL = "agricultural"
    ALLOTMENT_HOUSE = "allotment_house"
    APARTMENTS = "apartments"
    BARN = "barn"
    BEACH_HUT = "beach_hut"
    BOATHOUSE = "boathouse"
    BRIDGE_STRUCTURE = "bridge_structure"
    BUNGALOW = "bungalow"
    BUNKER = "bunker"
    CABIN = "cabin"
    CARAVAN = "caravan"
    CATHEDRAL = "cathedral"
    CHAPEL = "chapel"
    CHURCH = "church"
    CIVIC = "civic"
    COLLEGE = "college"
    COMMERCIAL = "commercial"
    CONSERVATORY = "conservatory"
    COWSHED = "cowshed"
    DETACHED = "detached"
    DETACHED_HOUSE = "detached_house"
    DORMITORY = "dormitory"
    FARM = "farm"
    FARM_AUXILIARY = "farm_auxiliary"
    FIRE_STATION = "fire_station"
    GARAGE = "garage"
    GARAGES = "garages"
    GOVERNMENT = "government"
    GRANDSTAND = "grandstand"
    GREENHOUSE = "greenhouse"
    HANGAR = "hangar"
    HOSPITAL = "hospital"
    HOTEL = "hotel"
    HOUSE = "house"
    HOUSEBOAT = "houseboat"
    HUT = "hut"
    INDUSTRIAL = "industrial"
    KINDERGARTEN = "kindergarten"
    KIOSK = "kiosk"
    LIBRARY = "library"
    MANUFACTURE = "manufacture"
    MOBILE_HOME = "mobile_home"
    MOSQUE = "mosque"
    OFFICE = "office"
    OFFICES = "offices"
    PARKING = "parking"
    PAVILION = "pavilion"
    PRISON = "prison"
    PUBLIC = "public"
    RELIGIOUS = "religious"
    RESIDENTIAL = "residential"
    RETAIL = "retail"
    ROOF = "roof"
    RUINS = "ruins"
    SCHOOL = "school"
    SEMI = "semi"
    SEMIDETACHED_HOUSE = "semidetached_house"
    SERVICE = "service"
    SHED = "shed"
    SHRINE = "shrine"
    SILO = "silo"
    SLURRY_TANK = "slurry_tank"
    SPORTS_CENTRE = "sports_centre"
    SPORTS_HALL = "sports_hall"
    STABLE = "stable"
    STADIUM = "stadium"
    STATIC_CARAVAN = "static_caravan"
    STILT_HOUSE = "stilt_house"
    STORAGE_TANK = "storage_tank"
    STY = "sty"
    SUPERMARKET = "supermarket"
    SYNAGOGUE = "synagogue"
    TEMPLE = "temple"
    TERRACE = "terrace"
    TOILETS = "toilets"
    TRAIN_STATION = "train_station"
    TRANSFORMER_TOWER = "transformer_tower"
    TRANSPORTATION = "transportation"
    TRULLO = "trullo"
    UNIVERSITY = "university"
    WAREHOUSE = "warehouse"
    WAYSIDE_SHRINE = "wayside_shrine"


class FacadeMaterial(str, Enum):
    """Building facade material classification."""

    BRICK = "brick"
    CEMENT_BLOCK = "cement_block"
    CLAY = "clay"
    CONCRETE = "concrete"
    GLASS = "glass"
    METAL = "metal"
    PLASTER = "plaster"
    PLASTIC = "plastic"
    STONE = "stone"
    TIMBER_FRAMING = "timber_framing"
    WOOD = "wood"


class RoofMaterial(str, Enum):
    """Building roof material classification."""

    CONCRETE = "concrete"
    COPPER = "copper"
    ETERNIT = "eternit"
    GLASS = "glass"
    GRASS = "grass"
    GRAVEL = "gravel"
    METAL = "metal"
    PLASTIC = "plastic"
    ROOF_TILES = "roof_tiles"
    SLATE = "slate"
    SOLAR_PANELS = "solar_panels"
    THATCH = "thatch"
    TAR_PAPER = "tar_paper"
    WOOD = "wood"


class RoofShape(str, Enum):
    """Building roof shape classification."""

    DOME = "dome"
    FLAT = "flat"
    GABLED = "gabled"
    GAMBREL = "gambrel"
    HALF_HIPPED = "half_hipped"
    HIPPED = "hipped"
    MANSARD = "mansard"
    ONION = "onion"
    PYRAMIDAL = "pyramidal"
    ROUND = "round"
    SALTBOX = "saltbox"
    SAWTOOTH = "sawtooth"
    SKILLION = "skillion"
    SPHERICAL = "spherical"


class RoofOrientation(str, Enum):
    """Building roof orientation classification."""

    ACROSS = "across"
    ALONG = "along"


class BuildingPart(BaseModel):
    """Building part information."""

    facade_color: Optional[str] = Field(None, description="Facade color")
    facade_material: Optional[str] = Field(None, description="Facade material")
    roof_color: Optional[str] = Field(None, description="Roof color")
    roof_material: Optional[str] = Field(None, description="Roof material")
    roof_shape: Optional[str] = Field(None, description="Roof shape")


class PhysicalProperties(BaseModel):
    """Physical properties of buildings."""

    height: Optional[float] = Field(None, ge=0, description="Building height in meters")
    num_floors: Optional[int] = Field(None, ge=0, description="Number of floors")
    num_floors_underground: Optional[int] = Field(
        None, ge=0, description="Number of underground floors"
    )
    facade_color: Optional[str] = Field(None, description="Primary facade color")
    facade_material: Optional[str] = Field(None, description="Primary facade material")
    roof_color: Optional[str] = Field(None, description="Primary roof color")
    roof_material: Optional[str] = Field(None, description="Primary roof material")
    roof_shape: Optional[str] = Field(None, description="Primary roof shape")


class ConfidenceLevel(str, Enum):
    """Confidence levels for building data."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class BaseBuildingProperties(OvertureFeatureProperties):
    """Base properties shared by all building types."""

    # Override theme with constraint-based validation
    theme: theme_literal("buildings") = Field("buildings", description="Feature theme")

    # Required properties
    subtype: Optional[BuildingSubtype] = Field(None, description="Building subtype")

    # Optional complex containers
    names: Optional[NamesContainer] = Field(None, description="Multilingual names")
    address: Optional[AddressContainer] = Field(None, description="Address information")

    # Override sources to use advanced source items
    sources: Optional[List[AdvancedSourceItem]] = Field(
        None, min_length=1, description="Advanced source information"
    )

    # Optional numeric properties
    height: Optional[float] = Field(
        None, gt=0, description="Height of the building in meters"
    )
    num_floors: Optional[int] = Field(
        None, gt=0, description="Number of above-ground floors"
    )
    num_floors_underground: Optional[int] = Field(
        None, gt=0, description="Number of below-ground floors"
    )
    min_height: Optional[float] = Field(
        None, description="Building bottom height in meters"
    )
    min_floor: Optional[int] = Field(
        None, gt=0, description="Start floor if building is floating"
    )
    roof_height: Optional[float] = Field(None, description="Roof height in meters")
    roof_direction: Optional[float] = Field(
        None, ge=0, lt=360, description="Roof bearing in degrees"
    )
    level: Optional[int] = Field(None, description="Z-order level")

    # Optional boolean properties
    has_parts: Optional[bool] = Field(None, description="Building has parts")
    is_underground: Optional[bool] = Field(
        None, description="Entire building is below ground"
    )

    # Optional classification properties
    building_class: Optional[BuildingClass] = Field(
        None, alias="class", description="Building class"
    )
    facade_material: Optional[FacadeMaterial] = Field(
        None, description="Facade material"
    )
    roof_material: Optional[RoofMaterial] = Field(None, description="Roof material")
    roof_shape: Optional[RoofShape] = Field(None, description="Roof shape")
    roof_orientation: Optional[RoofOrientation] = Field(
        None, description="Roof orientation"
    )

    # Optional color properties (hexadecimal strings)
    facade_color: Optional[HexColor] = Field(None, description="Facade color (hex)")
    roof_color: Optional[HexColor] = Field(None, description="Roof color (hex)")


__all__ = [
    "BuildingSubtype",
    "BuildingClass",
    "FacadeMaterial",
    "RoofMaterial",
    "RoofShape",
    "RoofOrientation",
    "BuildingPart",
    "PhysicalProperties",
    "ConfidenceLevel",
    "BaseBuildingProperties",
]
