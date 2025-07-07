"""Place feature models for Overture Maps places theme."""

import re
from typing import Annotated, Any, Dict, List, Optional

from pydantic import AnyUrl, BaseModel, EmailStr, Field

from overture.schema.core.base import (
    OvertureFeature,
    OvertureFeatureProperties,
    register_model,
)
from overture.schema.core.common import (
    AddressContainer,
    AdvancedSourceItem,
    NamesContainer,
)
from overture.schema.validation import (
    GeometryTypeConstraint,
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
    alternate: Optional[
        Annotated[List[CategoryPattern], UniqueItemsConstraint(), MinItemsConstraint(1)]
    ] = Field(None, description="Alternate categories")


class PlaceBrand(BaseModel):
    """Brand information for places."""

    names: NamesContainer = Field(..., description="Multilingual brand names")
    wikidata: Optional[WikidataId] = Field(None, description="Wikidata identifier")


class PlaceContact(BaseModel):
    """Contact information for places."""

    phone: Optional[PhoneNumber] = Field(
        None,
        description="Phone number in international format",
    )
    email: Optional[EmailStr] = Field(None, description="Email address")
    website: Optional[AnyUrl] = Field(None, description="Website URL")
    social_media: Optional[Dict[str, AnyUrl]] = Field(
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

    monday: Optional[HoursFormat] = Field(None, description="Monday hours")
    tuesday: Optional[HoursFormat] = Field(None, description="Tuesday hours")
    wednesday: Optional[HoursFormat] = Field(None, description="Wednesday hours")
    thursday: Optional[HoursFormat] = Field(None, description="Thursday hours")
    friday: Optional[HoursFormat] = Field(None, description="Friday hours")
    saturday: Optional[HoursFormat] = Field(None, description="Saturday hours")
    sunday: Optional[HoursFormat] = Field(None, description="Sunday hours")


class PlaceConfidence(BaseModel):
    """Confidence scores for place data."""

    overall: Optional[ConfidenceScore] = Field(None, description="Overall confidence")
    location: Optional[ConfidenceScore] = Field(None, description="Location confidence")
    name: Optional[ConfidenceScore] = Field(None, description="Name confidence")
    categories: Optional[ConfidenceScore] = Field(
        None, description="Categories confidence"
    )


class PlaceProperties(OvertureFeatureProperties):
    """Properties specific to place features."""

    # Override theme and type with constraint-based validation
    theme: theme_literal("places") = Field("places", description="Feature theme")
    type: type_literal("place") = Field("place", description="Feature type")

    # Optional properties
    categories: Optional[PlaceCategories] = Field(None, description="Place categories")

    # Optional complex containers
    names: Optional[NamesContainer] = Field(None, description="Multilingual names")
    brand: Optional[PlaceBrand] = Field(None, description="Brand information")
    addresses: Optional[Annotated[List[AddressContainer], MinItemsConstraint(1)]] = (
        Field(None, description="Place addresses")
    )

    # Override sources to use advanced source items
    sources: Optional[Annotated[List[AdvancedSourceItem], MinItemsConstraint(1)]] = (
        Field(None, description="Advanced source information")
    )

    # Contact information
    websites: Optional[
        Annotated[List[str], UniqueItemsConstraint(), MinItemsConstraint(1)]
    ] = Field(None, description="Website URLs")
    socials: Optional[
        Annotated[List[str], UniqueItemsConstraint(), MinItemsConstraint(1)]
    ] = Field(None, description="Social media URLs")
    emails: Optional[
        Annotated[List[EmailStr], UniqueItemsConstraint(), MinItemsConstraint(1)]
    ] = Field(None, description="Email addresses")
    phones: Optional[
        Annotated[List[PhoneNumber], UniqueItemsConstraint(), MinItemsConstraint(1)]
    ] = Field(None, description="Phone numbers")

    # Quality indicators
    confidence: Optional[ConfidenceScore] = Field(
        None, description="Confidence score (0.0-1.0)"
    )


class PlaceFeature(OvertureFeature):
    """Place feature model."""

    properties: PlaceProperties = Field(..., description="Place feature properties")
    geometry: Annotated[Dict[str, Any], GeometryTypeConstraint(["Point"])] = Field(
        ..., description="GeoJSON geometry (Point)"
    )


# Register Pydantic models when module is imported

register_model("places", "place", PlaceFeature)
