"""Building part type models."""

# Register theme-type mappings for strict validation
from overture.schema.core.base import add_theme_type_mapping

from .models import BuildingPart

add_theme_type_mapping("buildings", "building_part")

__all__ = ["BuildingPart"]
