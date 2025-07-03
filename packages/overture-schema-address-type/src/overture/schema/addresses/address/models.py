"""Address feature models for Overture Maps addresses theme."""

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from overture.schema.core.base import (
    OvertureFeature,
    OvertureFeatureProperties,
    register_model,
)
from overture.schema.core.common import (
    AdvancedSourceItem,
)


class AddressLevel(BaseModel):
    """Single administrative level in address hierarchy."""

    value: Optional[str] = Field(
        None,
        pattern=r"^(\S.*)?\S$",
        min_length=1,
        description="Administrative level value (no leading/trailing whitespace)",
    )

    @field_validator("value")
    @classmethod
    def validate_value_whitespace(cls, v):
        """Ensure no leading or trailing whitespace."""
        if v is not None and (v.startswith(" ") or v.endswith(" ")):
            raise ValueError(
                "Address level value cannot have leading or trailing whitespace"
            )
        return v


class AddressProperties(OvertureFeatureProperties):
    """Properties specific to address features."""

    # Required properties
    country: str = Field(
        ..., pattern=r"^[A-Z]{2}$", description="ISO 3166-1 alpha-2 country code"
    )
    address_levels: List[AddressLevel] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="Administrative levels (1-5), ordered highest first",
    )

    # Optional address components
    postcode: Optional[str] = Field(
        None,
        pattern=r"^(\S.*)?\S$",
        min_length=1,
        description="Postal/ZIP code (no leading/trailing whitespace)",
    )
    street: Optional[str] = Field(
        None,
        pattern=r"^(\S.*)?\S$",
        min_length=1,
        description="Street name (no leading/trailing whitespace)",
    )
    number: Optional[str] = Field(
        None,
        pattern=r"^(\S.*)?\S$",
        min_length=1,
        description="House/building number (no leading/trailing whitespace)",
    )
    unit: Optional[str] = Field(
        None,
        pattern=r"^(\S.*)?\S$",
        min_length=1,
        description="Suite/apartment/floor number (no leading/trailing whitespace)",
    )
    postal_city: Optional[str] = Field(
        None,
        pattern=r"^(\S.*)?\S$",
        min_length=1,
        description="Alternative city name for mailing (no leading/trailing whitespace)",
    )

    # Sources
    sources: Optional[List[AdvancedSourceItem]] = Field(
        None, min_length=1, description="Advanced source information"
    )

    @field_validator("theme")
    @classmethod
    def validate_theme(cls, v):
        if v != "addresses":
            raise ValueError("Address theme must be 'addresses'")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v != "address":
            raise ValueError("Address type must be 'address'")
        return v

    @field_validator("address_levels")
    @classmethod
    def validate_address_levels(cls, v):
        """Validate address levels array constraints."""
        if not v:
            raise ValueError("Address must have at least one address level")

        if len(v) > 5:
            raise ValueError("Address cannot have more than 5 address levels")

        return v

    @field_validator("postcode")
    @classmethod
    def validate_postcode_whitespace(cls, v):
        """Ensure no leading or trailing whitespace."""
        if v is not None and (v.startswith(" ") or v.endswith(" ")):
            raise ValueError("Postcode cannot have leading or trailing whitespace")
        return v

    @field_validator("street")
    @classmethod
    def validate_street_whitespace(cls, v):
        """Ensure no leading or trailing whitespace."""
        if v is not None and (v.startswith(" ") or v.endswith(" ")):
            raise ValueError("Street cannot have leading or trailing whitespace")
        return v

    @field_validator("number")
    @classmethod
    def validate_number_whitespace(cls, v):
        """Ensure no leading or trailing whitespace."""
        if v is not None and (v.startswith(" ") or v.endswith(" ")):
            raise ValueError("Number cannot have leading or trailing whitespace")
        return v

    @field_validator("unit")
    @classmethod
    def validate_unit_whitespace(cls, v):
        """Ensure no leading or trailing whitespace."""
        if v is not None and (v.startswith(" ") or v.endswith(" ")):
            raise ValueError("Unit cannot have leading or trailing whitespace")
        return v

    @field_validator("postal_city")
    @classmethod
    def validate_postal_city_whitespace(cls, v):
        """Ensure no leading or trailing whitespace."""
        if v is not None and (v.startswith(" ") or v.endswith(" ")):
            raise ValueError("Postal city cannot have leading or trailing whitespace")
        return v


class AddressFeature(OvertureFeature):
    """Address feature model."""

    properties: AddressProperties = Field(..., description="Address feature properties")

    @field_validator("geometry")
    @classmethod
    def validate_geometry_type(cls, v):
        """Addresses must have Point geometry."""
        # Call parent validation first
        super().validate_geometry_structure(v)

        geom_type = v.get("type")
        if geom_type != "Point":
            raise ValueError(f"Address geometry must be Point, got {geom_type}")
        return v


# Register Pydantic models when module is imported

register_model("addresses", "address", AddressFeature)
