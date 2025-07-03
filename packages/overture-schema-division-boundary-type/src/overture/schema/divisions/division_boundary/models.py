"""Division boundary models for Overture Maps divisions theme."""

from typing import List, Optional

from pydantic import Field, field_validator, model_validator

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

    # Required properties
    subtype: PlaceType = Field(..., description="Administrative level")
    class_: AreaBoundaryClass = Field(
        ..., alias="class", description="Boundary class (land/maritime)"
    )
    division_ids: List[str] = Field(
        ..., min_length=2, max_length=2, description="Two division IDs (left/right)"
    )

    # Geographic context
    country: Optional[str] = Field(
        None,
        pattern=r"^[A-Z]{2}$",
        description="ISO 3166-1 alpha-2 country code (not for country boundaries)",
    )
    region: Optional[str] = Field(
        None, pattern=r"^[A-Z]{2}-[A-Z0-9]{1,3}$", description="ISO 3166-2 region code"
    )

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

    @field_validator("theme")
    @classmethod
    def validate_theme(cls, v):
        if v != "divisions":
            raise ValueError("Division boundary theme must be 'divisions'")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v != "division_boundary":
            raise ValueError("Division boundary type must be 'division_boundary'")
        return v

    @field_validator("division_ids")
    @classmethod
    def validate_division_ids_unique(cls, v):
        """Ensure division IDs are unique."""
        if len(v) != len(set(v)):
            raise ValueError("Division IDs must be unique")
        return v

    @field_validator("is_territorial")
    @classmethod
    def validate_territorial_exclusive(cls, v, info):
        """Ensure is_land and is_territorial are mutually exclusive."""
        if v is not None and hasattr(info, "data") and "is_land" in info.data:
            is_land = info.data["is_land"]
            if is_land is not None and v and is_land:
                raise ValueError("is_land and is_territorial cannot both be true")
        return v

    @model_validator(mode="after")
    def validate_country_required_for_non_country(self):
        """Country is required for division boundaries except for country boundaries."""
        if self.country is None and self.subtype != PlaceType.COUNTRY:
            raise ValueError("Division boundary must have country property")
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
