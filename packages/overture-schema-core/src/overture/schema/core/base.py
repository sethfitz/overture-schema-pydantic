"""Base schema classes for Overture Maps features."""

from __future__ import annotations

from abc import ABC
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, model_serializer, model_validator

from overture.schema.validation import (
    MinItemsConstraint,
)
from overture.schema.validation.types import (
    ISO8601DateTime,
    JSONPointer,
    LinearReferenceRange,
)

from .geometry import Geometry

# Registry for valid themes and feature types (extensible)
_VALID_THEMES: set[str] = set()
_VALID_FEATURE_TYPES: set[str] = set()

# Registry for theme-type compatibility (pluggable)
_THEME_TYPE_MAPPING: dict[str, set[str]] = {}

# Global registry for Pydantic feature models
_FEATURE_MODELS: dict[tuple[str, str], type[BaseModel]] = {}


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


class SourceItem(BaseModel):
    """Source information for a specific property with optional linear referencing."""

    property: JSONPointer = Field(..., description="JSON Pointer to the property")
    dataset: str = Field(..., description="Source dataset identifier")
    record_id: str | None = Field(None, description="Specific record within dataset")
    update_time: ISO8601DateTime | None = Field(
        None, description="When this property was last updated"
    )
    confidence: float | None = Field(
        None, ge=0, le=1, description="Confidence value for ML-derived data"
    )
    between: LinearReferenceRange | None = Field(
        None, description="Linear referencing range"
    )


class CartographyContainer(BaseModel):
    """Cartographic hints for optimal map display."""

    prominence: int | None = Field(
        None, ge=1, le=100, description="Feature significance/importance"
    )
    min_zoom: int | None = Field(
        None, ge=0, le=23, description="Minimum recommended zoom level"
    )
    max_zoom: int | None = Field(
        None, ge=0, le=23, description="Maximum recommended zoom level"
    )
    sort_key: int | None = Field(None, description="Drawing order (lower = on top)")


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


class OvertureFeature(ExtensibleBaseModel, ABC):
    """Base class for all Overture features."""

    id: str = Field(..., min_length=1, description="Feature identifier")
    geometry: Geometry = Field(..., description="Geometry")
    theme: str = Field(..., description="Top-level Overture theme")
    type: str = Field(..., description="Specific feature type within theme")
    version: int = Field(..., ge=0, description="Feature version number")
    sources: Annotated[list[SourceItem], MinItemsConstraint(1)] | None = Field(
        None, description="Source information"
    )

    @model_serializer(mode="wrap")
    def serialize_model(self, serializer, info):
        """Serialize to flattened structure for Python, GeoJSON for JSON."""
        # Get the default serialization
        data = serializer(self)

        # Check the serialization mode/context
        if info.mode == "json":
            # Transform to GeoJSON structure for JSON output
            return {
                "type": "Feature",
                "id": data.pop("id"),
                "geometry": data.pop("geometry"),
                "properties": data,  # All remaining fields go into properties
            }
        else:
            # Return flattened structure for Python output
            return data


def register_model(
    theme: str,
    feature_type: str,
    model_class: type[BaseModel],
) -> None:
    """Register a Pydantic model class for a specific theme/type combination."""
    _FEATURE_MODELS[(theme, feature_type)] = model_class


def get_registered_model(theme: str, feature_type: str) -> type[BaseModel] | None:
    """Get the registered Pydantic model for a theme/type combination."""
    return _FEATURE_MODELS.get((theme, feature_type))


def parse_feature(feature: dict[str, Any], mode: str = "json") -> dict[str, Any] | None:
    """
    Parse and validate a feature, returning the parsed representation in specified mode.

    Args:
        feature: Feature data (GeoJSON or flattened format)
        mode: Output mode - "json" for GeoJSON format, "python" for flattened format

    Returns:
        Parsed feature in the specified format

    Supports both GeoJSON format (with nested properties) and flattened format.
    """
    try:
        # Basic structure validation
        if not isinstance(feature, dict):
            raise ValueError("Feature must be an object")

        # Detect format and normalize to flattened structure
        if "properties" in feature and feature.get("type") == "Feature":
            # GeoJSON format - flatten it
            flattened_feature = {
                "id": feature["id"],
                "geometry": feature["geometry"],
                **feature["properties"],  # Flatten properties into top level
            }
        else:
            # Already flattened format
            flattened_feature = feature.copy()

        theme = flattened_feature.get("theme")
        feature_type = flattened_feature.get("type")

        # Basic required field validation
        if not theme:
            raise ValueError("Missing required field: theme")
        if not feature_type:
            raise ValueError("Missing required field: type")

        # Check if theme and feature type are registered
        if not validate_theme(theme):
            raise ValueError(f"Unknown theme: {theme}")

        if not validate_feature_type(feature_type):
            raise ValueError(f"Unknown feature type: {feature_type}")

        # Try theme-type compatibility validation first
        if not validate_theme_type_compatibility(theme, feature_type):
            raise ValueError(
                f"Invalid theme-type combination: theme='{theme}', type='{feature_type}'"
            )

        # Look up registered Pydantic model
        model_class = get_registered_model(theme, feature_type)
        if model_class:
            try:
                # Parse with Pydantic model using flattened structure
                parsed_model = model_class.model_validate(flattened_feature)
                # Return in requested mode
                return parsed_model.model_dump(
                    exclude_none=True, mode=mode, by_alias=True
                )
            except Exception as e:
                raise ValueError(f"Pydantic validation failed: {str(e)}") from e

        # If no model is registered, it's an error
        raise ValueError(
            f"No registered model found for theme='{theme}', type='{feature_type}'"
        )

    except Exception as e:
        raise ValueError(str(e)) from e


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
