"""Building part type models."""

# Register theme-type mappings for strict validation
from overture.schema.core.base import add_theme_type_mapping

from .models import BuildingPartFeature, BuildingPartProperties

add_theme_type_mapping("buildings", "building_part")

__all__ = ["BuildingPartFeature", "BuildingPartProperties"]
