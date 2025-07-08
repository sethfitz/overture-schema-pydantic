"""Address feature models for Overture Maps addresses theme."""

# Register theme-type mappings for strict validation
from overture.schema.core.base import add_theme_type_mapping

from .models import (
    Address,
    AddressLevel,
    AddressProperties,
)

add_theme_type_mapping("addresses", "address")

__all__ = [
    "AddressLevel",
    "AddressProperties",
    "Address",
]
