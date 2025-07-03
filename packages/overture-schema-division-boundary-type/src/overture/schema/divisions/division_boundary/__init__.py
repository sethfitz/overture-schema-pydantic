"""Division boundary models for Overture Maps."""

# Register theme-type mappings for strict validation
from overture.schema.core.base import add_theme_type_mapping

from .models import DivisionBoundary, DivisionBoundaryProperties

add_theme_type_mapping("divisions", "division_boundary")

__all__ = ["DivisionBoundary", "DivisionBoundaryProperties"]
