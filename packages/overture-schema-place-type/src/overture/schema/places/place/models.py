"""Place feature models for Overture Maps places theme."""

import re
from typing import Annotated, Dict, List, Optional

from pydantic import AnyUrl, BaseModel, EmailStr, Field, field_validator

from overture.schema.validation import (
    CategoryPatternConstraint,
    UniqueItemsConstraint,
)

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
from overture.schema.validation.types import (
    CategoryPattern,
    theme_literal,
    type_literal,
)


class PlaceCategories(BaseModel):
    """Place categories with primary and alternate classification."""

    primary: CategoryPattern = Field(..., description="Primary category (required)")
    alternate: Optional[Annotated[List[CategoryPattern], UniqueItemsConstraint()]] = (
        Field(None, min_length=1, description="Alternate categories")
    )

    @field_validator("primary")
    @classmethod
    def validate_primary_not_empty(cls, v):
        """Ensure primary category is not empty."""
        if not v.strip():
            raise ValueError("Primary category cannot be empty")
        return v


class PlaceBrand(BaseModel):
    """Brand information for places."""

    names: NamesContainer = Field(..., description="Multilingual brand names")
    wikidata: Optional[str] = Field(
        None, pattern=r"^Q\d+$", description="Wikidata identifier"
    )


class PlaceContact(BaseModel):
    """Contact information for places."""

    phone: Optional[str] = Field(
        None,
        pattern=r"^\+\d{1,3}[\s\-\(\)0-9]+$",
        description="Phone number in international format",
    )
    email: Optional[EmailStr] = Field(None, description="Email address")
    website: Optional[AnyUrl] = Field(None, description="Website URL")
    social_media: Optional[Dict[str, AnyUrl]] = Field(
        None, description="Social media profiles"
    )

    @field_validator("social_media")
    @classmethod
    def validate_social_media_keys(cls, v):
        """Validate social media platform keys."""
        if v is None:
            return v

        valid_platforms = {
            "facebook",
            "twitter",
            "instagram",
            "linkedin",
            "youtube",
            "tiktok",
            "pinterest",
            "snapchat",
        }

        for platform in v.keys():
            if platform not in valid_platforms:
                raise ValueError(f"Invalid social media platform: {platform}")

        return v


class PlaceOperatingHours(BaseModel):
    """Operating hours for places."""

    monday: Optional[str] = Field(None, description="Monday hours")
    tuesday: Optional[str] = Field(None, description="Tuesday hours")
    wednesday: Optional[str] = Field(None, description="Wednesday hours")
    thursday: Optional[str] = Field(None, description="Thursday hours")
    friday: Optional[str] = Field(None, description="Friday hours")
    saturday: Optional[str] = Field(None, description="Saturday hours")
    sunday: Optional[str] = Field(None, description="Sunday hours")

    @field_validator(
        "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
    )
    @classmethod
    def validate_hours_format(cls, v):
        """Validate hours format (e.g., '09:00-17:00' or 'closed')."""
        if v is None:
            return v

        if v.lower() in ["closed", "24/7", "24 hours"]:
            return v

        # Simple validation for HH:MM-HH:MM format
        pattern = re.compile(r"^\d{2}:\d{2}-\d{2}:\d{2}$")
        if not pattern.match(v):
            raise ValueError(
                f"Invalid hours format: {v}. Expected 'HH:MM-HH:MM' or 'closed'"
            )

        return v


class PlaceConfidence(BaseModel):
    """Confidence scores for place data."""

    overall: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Overall confidence"
    )
    location: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Location confidence"
    )
    name: Optional[float] = Field(None, ge=0.0, le=1.0, description="Name confidence")
    categories: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Categories confidence"
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
    addresses: Optional[List[AddressContainer]] = Field(
        None, min_length=1, description="Place addresses"
    )

    # Override sources to use advanced source items
    sources: Optional[List[AdvancedSourceItem]] = Field(
        None, min_length=1, description="Advanced source information"
    )

    # Contact information
    websites: Optional[Annotated[List[str], UniqueItemsConstraint()]] = Field(
        None, min_length=1, description="Website URLs"
    )
    socials: Optional[Annotated[List[str], UniqueItemsConstraint()]] = Field(
        None, min_length=1, description="Social media URLs"
    )
    emails: Optional[Annotated[List[EmailStr], UniqueItemsConstraint()]] = Field(
        None, min_length=1, description="Email addresses"
    )
    phones: Optional[Annotated[List[str], UniqueItemsConstraint()]] = Field(
        None, min_length=1, description="Phone numbers"
    )

    # Quality indicators
    confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Confidence score (0.0-1.0)"
    )


class PlaceFeature(OvertureFeature):
    """Place feature model."""

    properties: PlaceProperties = Field(..., description="Place feature properties")

    @field_validator("geometry")
    @classmethod
    def validate_geometry_type(cls, v):
        """Places must have Point geometry."""
        # Call parent validation first
        super().validate_geometry_structure(v)

        geom_type = v.get("type")
        if geom_type != "Point":
            raise ValueError(f"Place geometry must be Point, got {geom_type}")
        return v


# Register Pydantic models when module is imported

register_model("places", "place", PlaceFeature)
