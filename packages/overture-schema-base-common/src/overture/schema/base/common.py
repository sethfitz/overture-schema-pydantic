"""Common structures and enums shared across base theme types."""

from enum import Enum
from typing import List, Optional

from pydantic import field_validator

from overture.schema.core.base import OvertureFeatureProperties


class SurfaceMaterial(str, Enum):
    """Surface material enum used by infrastructure and land features."""

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
    SETT = "sett"
    TARTAN = "tartan"
    UNPAVED = "unpaved"
    WOOD = "wood"
    WOODCHIPS = "woodchips"


class BaseGeometryType(str, Enum):
    """Supported geometry types for base theme features."""

    POINT = "Point"
    LINESTRING = "LineString"
    POLYGON = "Polygon"
    MULTIPOINT = "MultiPoint"
    MULTILINESTRING = "MultiLineString"
    MULTIPOLYGON = "MultiPolygon"


class BaseThemeProperties(OvertureFeatureProperties):
    """Base properties for all base theme features."""

    # Common surface property that can be used by infrastructure and land
    surface: Optional[SurfaceMaterial] = None

    @field_validator("theme")
    @classmethod
    def validate_theme_is_base(cls, v):
        if v != "base":
            raise ValueError("Base theme feature must have theme='base'")
        return v


def create_geometry_validator(valid_types: List[str]):
    """Factory function to create geometry validators for specific geometry types."""

    def validate_geometry_type(cls, v):
        """Validate geometry type matches expected types."""
        # Call parent validation first
        super(cls, cls).validate_geometry_structure(v)

        geom_type = v.get("type")
        if geom_type not in valid_types:
            return ValueError(f"Geometry must be one of {valid_types}, got {geom_type}")
        return v

    return validate_geometry_type


__all__ = [
    "SurfaceMaterial",
    "BaseGeometryType",
    "BaseThemeProperties",
    "create_geometry_validator",
]
