"""Division models for Overture Maps divisions theme."""

from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator, model_validator

from overture.schema.core.base import (
    OvertureFeature,
    OvertureFeatureProperties,
    register_model,
)
from overture.schema.core.common import (
    AdvancedSourceItem,
    NamesContainer,
)
from overture.schema.divisions.common.models import (
    DivisionClass,
    HierarchyItem,
    Norms,
    Perspectives,
    PlaceType,
)


class DivisionProperties(OvertureFeatureProperties):
    """Properties specific to division features."""

    # Required properties
    subtype: PlaceType = Field(..., description="Administrative level")

    # Administrative hierarchy
    hierarchies: List[List[HierarchyItem]] = Field(
        ..., min_length=1, description="Administrative hierarchy chains"
    )

    # Geographic context
    country: str = Field(
        ..., pattern=r"^[A-Z]{2}$", description="ISO 3166-1 alpha-2 country code"
    )
    region: Optional[str] = Field(
        None, pattern=r"^[A-Z]{2}-[A-Z0-9]{1,3}$", description="ISO 3166-2 region code"
    )

    # Relationships
    parent_division_id: Optional[str] = Field(
        None, min_length=1, pattern=r"^\S+$", description="Parent division identifier"
    )
    capital_division_ids: Optional[List[str]] = Field(
        None, min_length=1, description="Capital division identifiers"
    )
    capital_of_divisions: Optional[List[Dict[str, Any]]] = Field(
        None, min_length=1, description="Divisions this is capital of"
    )

    # Political and social context
    perspectives: Optional[Perspectives] = Field(
        None, description="Political perspectives"
    )
    norms: Optional[Norms] = Field(None, description="Local norms")

    # Localization
    local_type: Optional[Dict[str, str]] = Field(
        None, description="Localized subtype name"
    )

    # Population and ranking
    population: Optional[int] = Field(None, ge=0, description="Population count")
    prominence: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Prominence score (0.0-1.0)"
    )

    # Optional classification
    class_: Optional[DivisionClass] = Field(
        None, alias="class", description="Division class designation"
    )

    # Complex containers
    names: Optional[NamesContainer] = Field(None, description="Multilingual names")
    sources: Optional[List[AdvancedSourceItem]] = Field(
        None, min_length=1, description="Advanced source information"
    )

    @field_validator("theme")
    @classmethod
    def validate_theme(cls, v):
        if v != "divisions":
            raise ValueError("Division theme must be 'divisions'")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v != "division":
            raise ValueError("Division type must be 'division'")
        return v

    @field_validator("hierarchies")
    @classmethod
    def validate_hierarchies(cls, v):
        """Validate hierarchy structure and consistency."""
        if not v:
            raise ValueError("Division must have at least one hierarchy")

        for hierarchy in v:
            if not hierarchy:
                raise ValueError("Hierarchy cannot be empty")

            # Validate hierarchy item uniqueness within each hierarchy
            division_ids = [item.division_id for item in hierarchy]
            if len(division_ids) != len(set(division_ids)):
                raise ValueError("Division IDs must be unique within hierarchy")

        return v

    @model_validator(mode="after")
    def validate_parent_division_id_required(self):
        """Validate parent division based on subtype."""
        subtype = self.subtype
        parent_division_id = self.parent_division_id

        if subtype == PlaceType.COUNTRY and parent_division_id is not None:
            raise ValueError("Countries must not have parent_division_id")
        elif subtype != PlaceType.COUNTRY and parent_division_id is None:
            raise ValueError(
                f"parent_division_id is required for sub-country divisions (subtype: {subtype})"
            )

        return self

    @field_validator("capital_division_ids")
    @classmethod
    def validate_capital_division_ids_unique(cls, v):
        """Ensure capital division IDs are unique."""
        if v is None:
            return v

        if len(v) != len(set(v)):
            raise ValueError("Capital division IDs must be unique")

        return v

    @field_validator("capital_division_ids")
    @classmethod
    def validate_capital_division_ids_not_whitespace(cls, v):
        """Reject whitespace-only capital division IDs."""
        if v is None:
            return v

        import re

        pattern = re.compile(r"^\S+$")
        for div_id in v:
            if not pattern.match(div_id):
                raise ValueError(f"'{div_id}' does not match pattern")

        return v

    @field_validator("capital_of_divisions")
    @classmethod
    def validate_capital_of_divisions_unique(cls, v):
        """Ensure capital of divisions are unique."""
        if v is None:
            return v

        # Check uniqueness based on division_id
        division_ids = [item.get("division_id") for item in v if isinstance(item, dict)]
        if len(division_ids) != len(set(division_ids)):
            raise ValueError("Capital of divisions must be unique")

        return v


class Division(OvertureFeature):
    """Division feature model."""

    properties: DivisionProperties = Field(
        ..., description="Division feature properties"
    )

    @field_validator("geometry")
    @classmethod
    def validate_geometry_type(cls, v):
        """Divisions must have Point geometry."""
        # Call parent validation first
        super().validate_geometry_structure(v)

        geom_type = v.get("type")
        if geom_type != "Point":
            raise ValueError(f"Division geometry must be Point, got {geom_type}")

        # Validate Point coordinates
        if "coordinates" in v:
            coords = v["coordinates"]
            if not isinstance(coords, list) or len(coords) < 2:
                raise ValueError(
                    "Point coordinates must be an array with at least 2 elements"
                )

            # Check that coordinates are numbers
            for i, coord in enumerate(coords):
                if not isinstance(coord, (int, float)):
                    raise ValueError(
                        f"Coordinate {i} must be a number, got {type(coord).__name__}"
                    )

        return v


# Register the model
register_model("divisions", "division", Division)
