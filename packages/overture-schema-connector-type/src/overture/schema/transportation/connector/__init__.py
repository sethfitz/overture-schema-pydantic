"""Connector type models for Overture Maps."""

# Register theme-type mappings for strict validation
from overture.schema.core.base import add_theme_type_mapping

from .models import ConnectorFeature, ConnectorProperties

add_theme_type_mapping("transportation", "connector")

__all__ = ["ConnectorFeature", "ConnectorProperties"]
