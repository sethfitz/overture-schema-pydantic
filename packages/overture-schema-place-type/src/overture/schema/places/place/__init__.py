"""Place type models for Overture Maps places theme."""

# Register theme-type mappings for strict validation
from overture.schema.core.base import add_theme_type_mapping

from .models import (
    Place,
    PlaceBrand,
    PlaceCategories,
    PlaceConfidence,
    PlaceContact,
    PlaceOperatingHours,
)

add_theme_type_mapping("places", "place")

__all__ = [
    "Place",
    "PlaceCategories",
    "PlaceBrand",
    "PlaceContact",
    "PlaceOperatingHours",
    "PlaceConfidence",
]
