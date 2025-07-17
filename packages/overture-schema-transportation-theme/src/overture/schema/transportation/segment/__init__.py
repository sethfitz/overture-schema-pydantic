"""Segment type models for Overture Maps."""

# Register theme-type mappings for strict validation
from overture.schema.core.base import add_theme_type_mapping

from .models import Segment

add_theme_type_mapping("transportation", "segment")

__all__ = ["Segment"]
