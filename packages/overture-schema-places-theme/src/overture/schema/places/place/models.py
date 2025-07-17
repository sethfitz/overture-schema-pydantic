"""Place feature models for Overture Maps places theme."""

import re
from typing import Annotated

from pydantic import AnyUrl, BaseModel, EmailStr, Field

from overture.schema.core.base import (
    OvertureFeature,
    register_model,
)
from overture.schema.core.common import (
    AddressContainer,
    NamesContainer,
)
from overture.schema.core.geometry import Geometry, GeometryTypeConstraint
from overture.schema.validation import (
    MinItemsConstraint,
    PatternConstraint,
    UniqueItemsConstraint,
)
from overture.schema.validation.types import (
    CategoryPattern,
    ConfidenceScore,
    PhoneNumber,
    WikidataId,
    theme_literal,
    type_literal,
)


class PlaceCategories(BaseModel):
    """Place categories with primary and alternate classification."""

    primary: CategoryPattern = Field(..., description="Primary category (required)")
    alternate: Annotated[list[CategoryPattern], UniqueItemsConstraint(), MinItemsConstraint(1)] | None = Field(None, description="Alternate categories")


class PlaceBrand(BaseModel):
    """Brand information for places."""

    names: NamesContainer = Field(..., description="Multilingual brand names")
    wikidata: WikidataId | None = Field(None, description="Wikidata identifier")


class PlaceContact(BaseModel):
    """Contact information for places."""

    phone: PhoneNumber | None = Field(
        None,
        description="Phone number in international format",
    )
    email: EmailStr | None = Field(None, description="Email address")
    website: AnyUrl | None = Field(None, description="Website URL")
    social_media: dict[str, AnyUrl] | None = Field(
        None, description="Social media profiles"
    )


# Hours format constraint
HoursFormat = Annotated[
    str,
    PatternConstraint(
        r"^(\d{2}:\d{2}-\d{2}:\d{2}|closed|24/7|24 hours)$",
        "Hours must be in format 'HH:MM-HH:MM' or 'closed' or '24/7'",
        re.IGNORECASE,
    ),
]


class PlaceOperatingHours(BaseModel):
    """Operating hours for places."""

    monday: HoursFormat | None = Field(None, description="Monday hours")
    tuesday: HoursFormat | None = Field(None, description="Tuesday hours")
    wednesday: HoursFormat | None = Field(None, description="Wednesday hours")
    thursday: HoursFormat | None = Field(None, description="Thursday hours")
    friday: HoursFormat | None = Field(None, description="Friday hours")
    saturday: HoursFormat | None = Field(None, description="Saturday hours")
    sunday: HoursFormat | None = Field(None, description="Sunday hours")


class PlaceConfidence(BaseModel):
    """Confidence scores for place data."""

    overall: ConfidenceScore | None = Field(None, description="Overall confidence")
    location: ConfidenceScore | None = Field(None, description="Location confidence")
    name: ConfidenceScore | None = Field(None, description="Name confidence")
    categories: ConfidenceScore | None = Field(
        None, description="Categories confidence"
    )


class Place(OvertureFeature):
    """Place feature model."""

    # Override theme and type with constraint-based validation
    theme: theme_literal("places") = Field("places", description="Feature theme")
    type: type_literal("place") = Field("place", description="Feature type")

    # Optional properties
    categories: PlaceCategories | None = Field(None, description="Place categories")

    # Optional complex containers
    names: NamesContainer | None = Field(None, description="Multilingual names")
    brand: PlaceBrand | None = Field(None, description="Brand information")
    addresses: Annotated[list[AddressContainer], MinItemsConstraint(1)] | None = (
        Field(None, description="Place addresses")
    )

    # Contact information
    websites: Annotated[list[str], UniqueItemsConstraint(), MinItemsConstraint(1)] | None = Field(None, description="Website URLs")
    socials: Annotated[list[str], UniqueItemsConstraint(), MinItemsConstraint(1)] | None = Field(None, description="Social media URLs")
    emails: Annotated[list[EmailStr], UniqueItemsConstraint(), MinItemsConstraint(1)] | None = Field(None, description="Email addresses")
    phones: Annotated[list[PhoneNumber], UniqueItemsConstraint(), MinItemsConstraint(1)] | None = Field(None, description="Phone numbers")

    # Quality indicators
    confidence: ConfidenceScore | None = Field(
        None, description="Confidence score (0.0-1.0)"
    )

    # Geometry
    geometry: Annotated[Geometry, GeometryTypeConstraint("Point")] = Field(
        ..., description="Geometry (Point)"
    )


# Register Pydantic models when module is imported

register_model("places", "place", Place)
