"""Division feature models for Overture Maps divisions theme."""

# Register theme-type mappings for strict validation
from overture.schema.core.base import add_theme_type_mapping

from .models import Division

add_theme_type_mapping("divisions", "division")

__all__ = ["Division"]
