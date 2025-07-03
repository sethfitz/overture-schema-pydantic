"""Place type models for Overture Maps places theme."""

# Register theme-type mappings for strict validation
from overture.schema.core.base import add_theme_type_mapping

from .models import (
    PlaceBrand,
    PlaceCategories,
    PlaceConfidence,
    PlaceContact,
    PlaceFeature,
    PlaceOperatingHours,
    PlaceProperties,
)

add_theme_type_mapping("places", "place")

__all__ = [
    "PlaceFeature",
    "PlaceProperties",
    "PlaceCategories",
    "PlaceBrand",
    "PlaceContact",
    "PlaceOperatingHours",
    "PlaceConfidence",
]
