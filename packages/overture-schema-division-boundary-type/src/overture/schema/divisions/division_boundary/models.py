"""Division boundary models for Overture Maps divisions theme."""

from typing import Annotated, List, Optional

from pydantic import Field, field_validator, model_validator

from overture.schema.validation import (
    CountryCode,
    RegionCode,
    UniqueItemsConstraint,
    theme_literal,
    type_literal,
)

from overture.schema.core.base import (
    OvertureFeature,
    OvertureFeatureProperties,
    register_model,
)
from overture.schema.core.common import (
    AdvancedSourceItem,
)
from overture.schema.divisions.common.models import (
    AreaBoundaryClass,
    Perspectives,
    PlaceType,
)


class DivisionBoundaryProperties(OvertureFeatureProperties):
    """Properties specific to division boundary features."""

    # Override theme and type with constraint-based validation
    theme: theme_literal("divisions") = Field("divisions", description="Feature theme")
    type: type_literal("division_boundary") = Field(
        "division_boundary", description="Feature type"
    )

    # Required properties
    subtype: PlaceType = Field(..., description="Administrative level")
    class_: AreaBoundaryClass = Field(
        ..., alias="class", description="Boundary class (land/maritime)"
    )
    division_ids: Annotated[List[str], UniqueItemsConstraint()] = Field(
        ..., min_length=2, max_length=2, description="Two division IDs (left/right)"
    )

    # Geographic context
    country: Optional[CountryCode] = Field(
        None,
        description="ISO 3166-1 alpha-2 country code (not for country boundaries)",
    )
    region: Optional[RegionCode] = Field(None, description="ISO 3166-2 region code")

    # Territorial designation (exclusive or) - strict boolean validation
    is_land: Optional[bool] = Field(
        None, description="Land boundary designation", strict=True
    )
    is_territorial: Optional[bool] = Field(
        None, description="Territorial boundary designation", strict=True
    )

    # Dispute status
    is_disputed: Optional[bool] = Field(None, description="Boundary is disputed")

    # Political and social context
    perspectives: Optional[Perspectives] = Field(
        None, description="Political perspectives"
    )

    # Complex containers
    sources: Optional[List[AdvancedSourceItem]] = Field(
        None, min_length=1, description="Advanced source information"
    )

    @model_validator(mode="after")
    def validate_country_required_for_non_country(self):
        """Country is required for division boundaries except for country boundaries."""
        if self.country is None and self.subtype != PlaceType.COUNTRY:
            raise ValueError("Division boundary must have country property")
        return self

    @model_validator(mode="after")
    def validate_mutually_exclusive_territorial_flags(self):
        """Ensure is_land and is_territorial are mutually exclusive."""
        if self.is_land is True and self.is_territorial is True:
            raise ValueError(
                "is_land and is_territorial are mutually exclusive and cannot both be true"
            )
        return self


class DivisionBoundary(OvertureFeature):
    """Division boundary feature model."""

    properties: DivisionBoundaryProperties = Field(
        ..., description="Division boundary feature properties"
    )

    @field_validator("geometry")
    @classmethod
    def validate_geometry_type(cls, v):
        """Division boundaries must have LineString or MultiLineString geometry."""
        # Call parent validation first
        super().validate_geometry_structure(v)

        geom_type = v.get("type")
        if geom_type not in ["LineString", "MultiLineString"]:
            raise ValueError(
                f"Division boundary geometry must be LineString or MultiLineString, got {geom_type}"
            )

        # Validate coordinates structure
        if "coordinates" in v:
            coords = v["coordinates"]
            if not isinstance(coords, list):
                raise ValueError("Coordinates must be an array")

            # Basic numeric validation for nested coordinate arrays
            def validate_coords_recursive(coord_array):
                if isinstance(coord_array, list):
                    for item in coord_array:
                        if isinstance(item, list):
                            validate_coords_recursive(item)
                        elif not isinstance(item, (int, float)):
                            raise ValueError(
                                f"Coordinate must be a number, got {type(item).__name__}"
                            )

            validate_coords_recursive(coords)

        return v


# Register the model
register_model("divisions", "division_boundary", DivisionBoundary)
