"""Division area models for Overture Maps."""

# Register theme-type mappings for strict validation
from overture.schema.core.base import add_theme_type_mapping

from .models import DivisionArea

add_theme_type_mapping("divisions", "division_area")

__all__ = ["DivisionArea"]
