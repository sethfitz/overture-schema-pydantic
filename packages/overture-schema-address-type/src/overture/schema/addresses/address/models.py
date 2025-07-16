"""Address feature models for Overture Maps addresses theme."""

from typing import Annotated, List, Optional

from pydantic import BaseModel, Field

from overture.schema.core.base import (
    OvertureFeature,
    register_model,
)
from overture.schema.core.geometry import (
    Geometry,
    GeometryTypeConstraint,
)
from overture.schema.validation import (
    CountryCodeConstraint,
    MaxItemsConstraint,
    MinItemsConstraint,
    WhitespaceConstraint,
    theme_literal,
    type_literal,
)


class AddressLevel(BaseModel):
    """Single administrative level in address hierarchy."""

    value: Optional[Annotated[str, WhitespaceConstraint()]] = Field(
        None,
        min_length=1,
        description="Administrative level value (no leading/trailing whitespace)",
    )


class Address(OvertureFeature):
    """Address feature model."""

    # Override theme and type with constraint-based validation
    theme: theme_literal("addresses") = Field("addresses", description="Feature theme")
    type: type_literal("address") = Field("address", description="Feature type")

    # Required properties
    country: Annotated[str, CountryCodeConstraint()] = Field(
        ..., description="ISO 3166-1 alpha-2 country code"
    )
    address_levels: Annotated[
        List[AddressLevel], MinItemsConstraint(1), MaxItemsConstraint(5)
    ] = Field(
        ...,
        description="Administrative levels (1-5), ordered highest first",
    )

    # Optional address components
    postcode: Optional[Annotated[str, WhitespaceConstraint()]] = Field(
        None,
        min_length=1,
        description="Postal/ZIP code (no leading/trailing whitespace)",
    )
    street: Optional[Annotated[str, WhitespaceConstraint()]] = Field(
        None,
        min_length=1,
        description="Street name (no leading/trailing whitespace)",
    )
    number: Optional[Annotated[str, WhitespaceConstraint()]] = Field(
        None,
        min_length=1,
        description="House/building number (no leading/trailing whitespace)",
    )
    unit: Optional[Annotated[str, WhitespaceConstraint()]] = Field(
        None,
        min_length=1,
        description="Suite/apartment/floor number (no leading/trailing whitespace)",
    )
    postal_city: Optional[Annotated[str, WhitespaceConstraint()]] = Field(
        None,
        min_length=1,
        description="Alternative city name for mailing (no leading/trailing whitespace)",
    )

    # Geometry
    geometry: Annotated[Geometry, GeometryTypeConstraint("Point")] = Field(
        ..., description="Geometry (Point)"
    )


# Register Pydantic models when module is imported

register_model("addresses", "address", Address)
