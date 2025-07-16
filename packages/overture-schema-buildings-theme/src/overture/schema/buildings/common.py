"""Re-export common buildings structures from the buildings-common package."""

# Re-export everything from the buildings-common package for backward compatibility
from overture.schema.buildings.common import (
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
]
