"""Overture Schema Core package."""

from .validation_rules import (
    DiscriminatedUnionRule,
    EnumValidationRule,
    ExtensibleObjectRule,
    RequiredPropertyRule,
    UniqueArrayRule,
    ValidationRule,
    register_validation_rules,
    validate_with_rules,
)

__version__ = "0.1.0"

__all__ = [
    "ValidationRule",
    "EnumValidationRule",
    "UniqueArrayRule",
    "RequiredPropertyRule",
    "ExtensibleObjectRule",
    "DiscriminatedUnionRule",
    "validate_with_rules",
    "register_validation_rules",
]
