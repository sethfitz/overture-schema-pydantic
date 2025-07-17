"""Building type models for Overture Maps."""

# Re-export common structures for backward compatibility
# Register theme-type mappings for strict validation
from overture.schema.core.base import add_theme_type_mapping

from ..shared import (
    BuildingClass,
    BuildingPart,
    BuildingSubtype,
    ConfidenceLevel,
    FacadeMaterial,
    PhysicalProperties,
    RoofMaterial,
    RoofOrientation,
    RoofShape,
)
from .models import Building

add_theme_type_mapping("buildings", "building")

__all__ = [
    "Building",
    "BuildingSubtype",
    "BuildingClass",
    "FacadeMaterial",
    "RoofMaterial",
    "RoofShape",
    "RoofOrientation",
    "BuildingPart",
    "PhysicalProperties",
    "ConfidenceLevel",
]
