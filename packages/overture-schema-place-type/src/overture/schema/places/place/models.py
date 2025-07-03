"""Place feature models for Overture Maps places theme."""

import re
from typing import Dict, List, Optional

from pydantic import AnyUrl, BaseModel, EmailStr, Field, field_validator

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


class PlaceCategories(BaseModel):
    """Place categories with primary and alternate classification."""

    primary: str = Field(
        ...,
        pattern=r"^[a-z0-9]+(_[a-z0-9]+)*$",
        description="Primary category (required)",
    )
    alternate: Optional[List[str]] = Field(
        None, min_length=1, description="Alternate categories"
    )

    @field_validator("alternate")
    @classmethod
    def validate_alternate_unique(cls, v):
        """Ensure alternate categories are unique."""
        if v is None:
            return v

        if len(v) != len(set(v)):
            raise ValueError("Alternate categories must be unique")

        # Validate each alternate category pattern
        pattern = re.compile(r"^[a-z0-9]+(_[a-z0-9]+)*$")
        for category in v:
            if not pattern.match(category):
                raise ValueError(f"Invalid category format: {category}")

        return v

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
    websites: Optional[List[str]] = Field(
        None, min_length=1, description="Website URLs"
    )
    socials: Optional[List[str]] = Field(
        None, min_length=1, description="Social media URLs"
    )
    emails: Optional[List[EmailStr]] = Field(
        None, min_length=1, description="Email addresses"
    )
    phones: Optional[List[str]] = Field(None, min_length=1, description="Phone numbers")

    # Quality indicators
    confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Confidence score (0.0-1.0)"
    )

    @field_validator("theme")
    @classmethod
    def validate_theme(cls, v):
        if v != "places":
            raise ValueError("Place theme must be 'places'")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v != "place":
            raise ValueError("Place type must be 'place'")
        return v

    @field_validator("websites")
    @classmethod
    def validate_websites_unique(cls, v):
        """Ensure websites are unique."""
        if v is None:
            return v

        if len(v) != len(set(v)):
            raise ValueError("Websites must be unique")

        return v

    @field_validator("socials")
    @classmethod
    def validate_socials_unique(cls, v):
        """Ensure social URLs are unique."""
        if v is None:
            return v

        if len(v) != len(set(v)):
            raise ValueError("Social URLs must be unique")

        return v

    @field_validator("emails")
    @classmethod
    def validate_emails_unique(cls, v):
        """Ensure emails are unique."""
        if v is None:
            return v

        email_strings = [str(email) for email in v]
        if len(email_strings) != len(set(email_strings)):
            raise ValueError("Emails must be unique")

        return v

    @field_validator("phones")
    @classmethod
    def validate_phones_unique(cls, v):
        """Ensure phone numbers are unique."""
        if v is None:
            return v

        if len(v) != len(set(v)):
            raise ValueError("Phone numbers must be unique")

        return v


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
