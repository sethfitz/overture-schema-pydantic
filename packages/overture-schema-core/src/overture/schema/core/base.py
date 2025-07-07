"""Base schema classes for Overture Maps features."""

from __future__ import annotations

from abc import ABC
from typing import Annotated, Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from overture.schema.validation import (
    LiteralValueConstraint,
    MinItemsConstraint,
)
from overture.schema.validation.types import ISO8601DateTime, JSONPointer

from .validation_rules import validate_with_rules

# Registry for valid themes and feature types (extensible)
_VALID_THEMES: set[str] = set()
_VALID_FEATURE_TYPES: set[str] = set()

# Registry for theme-type compatibility (pluggable)
_THEME_TYPE_MAPPING: Dict[str, set[str]] = {}


def register_theme(theme: str) -> None:
    """Register a valid theme."""
    _VALID_THEMES.add(theme)


def register_feature_type(feature_type: str) -> None:
    """Register a valid feature type."""
    _VALID_FEATURE_TYPES.add(feature_type)


def register_theme_type_mapping(theme: str, feature_types: set[str]) -> None:
    """Register valid feature types for a theme."""
    _THEME_TYPE_MAPPING[theme] = feature_types


def add_theme_type_mapping(theme: str, feature_type: str) -> None:
    """Add a single feature type to a theme's valid types."""
    if theme not in _THEME_TYPE_MAPPING:
        _THEME_TYPE_MAPPING[theme] = set()
    _THEME_TYPE_MAPPING[theme].add(feature_type)


def get_valid_themes() -> set[str]:
    """Get all registered themes."""
    return _VALID_THEMES.copy()


def get_valid_feature_types() -> set[str]:
    """Get all registered feature types."""
    return _VALID_FEATURE_TYPES.copy()


def validate_theme(theme: str) -> bool:
    """Check if a theme is valid."""
    return theme in _VALID_THEMES


def validate_feature_type(feature_type: str) -> bool:
    """Check if a feature type is valid."""
    return feature_type in _VALID_FEATURE_TYPES


def validate_theme_type_compatibility(theme: str, feature_type: str) -> bool:
    """Check if a theme and feature type combination is valid."""
    # If no mappings are registered, allow all combinations
    if not _THEME_TYPE_MAPPING:
        return True

    # If theme has no registered mappings, allow all feature types for that theme
    if theme not in _THEME_TYPE_MAPPING:
        return True

    return feature_type in _THEME_TYPE_MAPPING[theme]


class SourcePropertyItem(BaseModel):
    """Source information for a specific property."""

    property: JSONPointer = Field(..., description="JSON Pointer to the property")
    dataset: str = Field(..., description="Source dataset identifier")
    record_id: Optional[str] = Field(None, description="Specific record within dataset")
    update_time: Optional[ISO8601DateTime] = Field(
        None, description="When this property was last updated"
    )
    confidence: Optional[float] = Field(
        None, ge=0, le=1, description="Confidence value for ML-derived data"
    )


class CartographyContainer(BaseModel):
    """Cartographic hints for optimal map display."""

    prominence: Optional[int] = Field(
        None, ge=1, le=100, description="Feature significance/importance"
    )
    min_zoom: Optional[int] = Field(
        None, ge=0, le=23, description="Minimum recommended zoom level"
    )
    max_zoom: Optional[int] = Field(
        None, ge=0, le=23, description="Maximum recommended zoom level"
    )
    sort_key: Optional[int] = Field(None, description="Drawing order (lower = on top)")


class ExtensibleBaseModel(BaseModel):
    """Base model that allows ext_* prefixed fields only."""

    model_config = ConfigDict(extra="allow")  # Allow extra fields for validation

    @model_validator(mode="after")
    def validate_extension_prefixes(self):
        """Validate that extra fields use allowed prefixes."""
        if hasattr(self, "__pydantic_extra__") and self.__pydantic_extra__:
            for field_name in self.__pydantic_extra__.keys():
                if not field_name.startswith("ext_"):
                    raise ValueError(
                        f"Unrecognized field '{field_name}' must use ext_ prefix"
                    )
        return self


class OvertureFeatureProperties(ExtensibleBaseModel):
    """Base properties for all Overture features."""

    theme: str = Field(..., description="Top-level Overture theme")
    type: str = Field(..., description="Specific feature type within theme")
    version: int = Field(..., ge=0, description="Feature version number")
    sources: Optional[Annotated[List[SourcePropertyItem], MinItemsConstraint(1)]] = (
        Field(None, description="Source information")
    )
    cartography: Optional[CartographyContainer] = Field(
        None, description="Cartographic display hints"
    )


class OvertureFeature(BaseModel, ABC):
    """Base class for all Overture features (GeoJSON Feature structure)."""

    id: str = Field(..., min_length=1, description="Feature identifier")
    type: Annotated[str, LiteralValueConstraint("Feature", "type")] = Field(
        "Feature", description="GeoJSON type"
    )
    geometry: Dict[str, Any] = Field(..., description="GeoJSON geometry")
    properties: OvertureFeatureProperties = Field(..., description="Feature properties")

    @classmethod
    def validate_geometry_structure(cls, v):
        """Basic geometry structure validation."""
        if not isinstance(v, dict):
            raise ValueError("geometry must be an object")
        if "type" not in v:
            raise ValueError("geometry must have a 'type' property")
        return v


# Global registry for Pydantic feature models
from typing import Type

_FEATURE_MODELS: Dict[tuple[str, str], Type[BaseModel]] = {}


def register_model(
    theme: str,
    feature_type: str,
    model_class: Type[BaseModel],
) -> None:
    """Register a Pydantic model class for a specific theme/type combination."""
    _FEATURE_MODELS[(theme, feature_type)] = model_class


def get_registered_model(theme: str, feature_type: str) -> Optional[Type[BaseModel]]:
    """Get the registered Pydantic model for a theme/type combination."""
    return _FEATURE_MODELS.get((theme, feature_type))


def validate_feature(feature: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate a feature dictionary against Overture schemas.

    This is the main validation function called by the test harness.
    Uses pure Pydantic model validation when available.
    """
    try:
        # Basic structure validation
        if not isinstance(feature, dict):
            return False, "Feature must be an object"

        if feature.get("type") != "Feature":
            return False, "Feature type must be 'Feature'"

        if "properties" not in feature:
            return False, "Feature must have properties"

        properties = feature["properties"]
        theme = properties.get("theme")
        feature_type = properties.get("type")

        # Check if theme and feature type are registered
        if theme and not validate_theme(theme):
            return False, f"Unknown theme: {theme}"

        if feature_type and not validate_feature_type(feature_type):
            return False, f"Unknown feature type: {feature_type}"

        # Try theme-type compatibility validation first
        if not validate_theme_type_compatibility(theme, feature_type):
            return (
                False,
                f"Invalid theme-type combination: theme='{theme}', type='{feature_type}'",
            )

        # Apply generic validation rules
        rule_valid, rule_error = validate_with_rules(theme, feature_type, feature)
        if not rule_valid:
            return False, rule_error

        # Look up registered Pydantic model
        model_class = get_registered_model(theme, feature_type)
        if model_class:
            try:
                model_class.model_validate(feature)
                return True, ""
            except Exception as e:
                return False, f"Pydantic validation failed: {str(e)}"

        # If theme and type are valid but no model is registered, accept for now
        # This allows for future extensibility
        return True, ""

    except Exception as e:
        return False, str(e)


def get_parsed_feature(feature: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse and validate a feature, returning the parsed dictionary representation.

    This function validates the feature and returns the dictionary representation
    of the parsed Pydantic model, which can be compared with the original.
    """
    try:
        # Basic structure validation
        if not isinstance(feature, dict):
            raise ValueError("Feature must be an object")

        if feature.get("type") != "Feature":
            raise ValueError("Feature type must be 'Feature'")

        if "properties" not in feature:
            raise ValueError("Feature must have properties")

        properties = feature["properties"]
        theme = properties.get("theme")
        feature_type = properties.get("type")

        # Check if theme and feature type are registered
        if theme and not validate_theme(theme):
            raise ValueError(f"Unknown theme: {theme}")

        if feature_type and not validate_feature_type(feature_type):
            raise ValueError(f"Unknown feature type: {feature_type}")

        # Try theme-type compatibility validation first
        if not validate_theme_type_compatibility(theme, feature_type):
            raise ValueError(
                f"Invalid theme-type combination: theme='{theme}', type='{feature_type}'"
            )

        # Apply generic validation rules
        rule_valid, rule_error = validate_with_rules(theme, feature_type, feature)
        if not rule_valid:
            raise ValueError(rule_error)

        # Look up registered Pydantic model
        model_class = get_registered_model(theme, feature_type)
        if model_class:
            try:
                # Parse with Pydantic model and return as dict
                parsed_model = model_class.model_validate(feature)
                return parsed_model.model_dump(
                    exclude_none=True, mode="json", by_alias=True
                )
            except Exception as e:
                raise ValueError(f"Pydantic validation failed: {str(e)}")

        # If no model is registered, return the original feature
        return feature

    except Exception as e:
        raise ValueError(str(e))


# Register core themes and feature types
register_theme("base")
register_theme("addresses")
register_theme("buildings")
register_theme("divisions")
register_theme("places")
register_theme("transportation")

register_feature_type("address")
register_feature_type("bathymetry")
register_feature_type("building")
register_feature_type("building_part")
register_feature_type("connector")
register_feature_type("division")
register_feature_type("division_area")
register_feature_type("division_boundary")
register_feature_type("infrastructure")
register_feature_type("land")
register_feature_type("land_cover")
register_feature_type("land_use")
register_feature_type("place")
register_feature_type("segment")
register_feature_type("water")

# Register bathymetry validator (temporary - should be in bathymetry package)
