"""LandUse feature models for Overture Maps base theme."""

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
from overture.schema.core.geometry import Geometry, GeometryTypeConstraint
from overture.schema.validation import (
    theme_literal,
    type_literal,
)


class LandUseSubtype(str, Enum):
    """Broad types of land use."""

    AGRICULTURE = "agriculture"
    AQUACULTURE = "aquaculture"
    CAMPGROUND = "campground"
    CEMETERY = "cemetery"
    CONSTRUCTION = "construction"
    DEVELOPED = "developed"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    GOLF = "golf"
    GRASS = "grass"
    HORTICULTURE = "horticulture"
    LANDFILL = "landfill"
    MANAGED = "managed"
    MEDICAL = "medical"
    MILITARY = "military"
    PARK = "park"
    PEDESTRIAN = "pedestrian"
    PROTECTED = "protected"
    RECREATION = "recreation"
    RELIGIOUS = "religious"
    RESIDENTIAL = "residential"
    RESOURCE_EXTRACTION = "resource_extraction"
    TRANSPORTATION = "transportation"
    WINTER_SPORTS = "winter_sports"


class LandUseClass(str, Enum):
    """Further classification of land use."""

    ABORIGINAL_LAND = "aboriginal_land"
    AIRFIELD = "airfield"
    ALLOTMENTS = "allotments"
    ANIMAL_KEEPING = "animal_keeping"
    AQUACULTURE = "aquaculture"
    BARRACKS = "barracks"
    BASE = "base"
    BEACH_RESORT = "beach_resort"
    BROWNFIELD = "brownfield"
    BUNKER = "bunker"
    CAMP_SITE = "camp_site"
    CEMETERY = "cemetery"
    CLINIC = "clinic"
    COLLEGE = "college"
    COMMERCIAL = "commercial"
    CONNECTION = "connection"
    CONSTRUCTION = "construction"
    DANGER_AREA = "danger_area"
    DOCTORS = "doctors"
    DOG_PARK = "dog_park"
    DOWNHILL = "downhill"
    DRIVING_RANGE = "driving_range"
    DRIVING_SCHOOL = "driving_school"
    EDUCATION = "education"
    ENVIRONMENTAL = "environmental"
    FAIRWAY = "fairway"
    FARMLAND = "farmland"
    FARMYARD = "farmyard"
    FATBIKE = "fatbike"
    FLOWERBED = "flowerbed"
    FOREST = "forest"
    GARAGES = "garages"
    GARDEN = "garden"
    GOLF_COURSE = "golf_course"
    GRASS = "grass"
    GRAVE_YARD = "grave_yard"
    GREEN = "green"
    GREENFIELD = "greenfield"
    GREENHOUSE_HORTICULTURE = "greenhouse_horticulture"
    HIGHWAY = "highway"
    HIKE = "hike"
    HOSPITAL = "hospital"
    ICE_SKATE = "ice_skate"
    INDUSTRIAL = "industrial"
    INSTITUTIONAL = "institutional"
    KINDERGARTEN = "kindergarten"
    LANDFILL = "landfill"
    LATERAL_WATER_HAZARD = "lateral_water_hazard"
    LOGGING = "logging"
    MARINA = "marina"
    MEADOW = "meadow"
    MILITARY = "military"
    MILITARY_HOSPITAL = "military_hospital"
    MILITARY_SCHOOL = "military_school"
    MUSIC_SCHOOL = "music_school"
    NATIONAL_PARK = "national_park"
    NATURAL_MONUMENT = "natural_monument"
    NATURE_RESERVE = "nature_reserve"
    NAVAL_BASE = "naval_base"
    NORDIC = "nordic"
    NUCLEAR_EXPLOSION_SITE = "nuclear_explosion_site"
    OBSTACLE_COURSE = "obstacle_course"
    ORCHARD = "orchard"
    PARK = "park"
    PEAT_CUTTING = "peat_cutting"
    PEDESTRIAN = "pedestrian"
    PITCH = "pitch"
    PLANT_NURSERY = "plant_nursery"
    PLAYGROUND = "playground"
    PLAZA = "plaza"
    PROTECTED = "protected"
    PROTECTED_LANDSCAPE_SEASCAPE = "protected_landscape_seascape"
    QUARRY = "quarry"
    RANGE = "range"
    RECREATION_GROUND = "recreation_ground"
    RELIGIOUS = "religious"
    RESIDENTIAL = "residential"
    RESORT = "resort"
    RETAIL = "retail"
    ROUGH = "rough"
    SALT_POND = "salt_pond"
    SCHOOL = "school"
    SCHOOLYARD = "schoolyard"
    SKI_JUMP = "ski_jump"
    SKITOUR = "skitour"
    SLED = "sled"
    SLEIGH = "sleigh"
    SNOW_PARK = "snow_park"
    SPECIES_MANAGEMENT_AREA = "species_management_area"
    STADIUM = "stadium"
    STATE_PARK = "state_park"
    STATIC_CARAVAN = "static_caravan"
    STRICT_NATURE_RESERVE = "strict_nature_reserve"
    TEE = "tee"
    THEME_PARK = "theme_park"
    TRACK = "track"
    TRAFFIC_ISLAND = "traffic_island"
    TRAINING_AREA = "training_area"
    TRENCH = "trench"
    UNIVERSITY = "university"
    VILLAGE_GREEN = "village_green"
    VINEYARD = "vineyard"
    WATER_HAZARD = "water_hazard"
    WATER_PARK = "water_park"
    WILDERNESS_AREA = "wilderness_area"
    WINTER_SPORTS = "winter_sports"
    WORKS = "works"
    ZOO = "zoo"


class LandUse(OvertureFeature):
    """LandUse feature model for classifications of human use of land."""

    # Override theme and type with constraint-based validation
    theme: theme_literal("base") = Field("base", description="Feature theme")
    type: type_literal("land_use") = Field("land_use", description="Feature type")

    # Required fields
    subtype: LandUseSubtype = Field(..., description="Broad type of land")
    class_: LandUseClass = Field(
        ..., alias="class", description="Further classification of the land use"
    )

    # Optional level field (from levelContainer)
    level: Optional[int] = Field(None, description="Z-order level")

    # Optional elevation and surface (from base defs)
    elevation: Optional[float] = Field(None, description="Elevation in meters")
    surface: Optional[SurfaceMaterial] = Field(None, description="Surface material")

    # Optional complex containers
    names: Optional[NamesContainer] = Field(None, description="Multilingual names")

    # Source tags from OpenStreetMap (from osmPropertiesContainer)
    source_tags: Optional[Dict[str, Any]] = Field(
        None, description="Source tags from data providers"
    )

    # Geometry constraints - Point, LineString, Polygon, or MultiPolygon
    geometry: Annotated[
        Geometry,
        GeometryTypeConstraint("Point", "LineString", "Polygon", "MultiPolygon"),
    ] = Field(
        ...,
        description="Geometry (Point, LineString, Polygon, or MultiPolygon)",
    )


# Register Pydantic models when module is imported
register_model("base", "land_use", LandUse)
