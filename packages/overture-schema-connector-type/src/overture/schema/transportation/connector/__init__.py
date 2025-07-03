"""Connector type models for Overture Maps."""

# Register theme-type mappings for strict validation
from overture.schema.core.base import add_theme_type_mapping

from .models import ConnectorFeature, ConnectorProperties

add_theme_type_mapping("transportation", "connector")

# Register validation rules for transportation connectors
from overture.schema.core.validation_rules import (
    DisallowedPropertyRule,
    UnrecognizedPropertyRule,
    register_validation_rules,
)

# Connector-specific validation rules
connector_rules = [
    # Level property is not allowed on connectors
    DisallowedPropertyRule("level", "level property is not allowed on connectors"),
    # Only allow recognized properties and ext_ prefixed properties
    UnrecognizedPropertyRule(
        {"theme", "type", "version", "sources", "cartography"},
        "Unrecognized property found",
    ),
]

register_validation_rules("transportation", "connector", connector_rules)

__all__ = ["ConnectorFeature", "ConnectorProperties"]
