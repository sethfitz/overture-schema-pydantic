"""Address-related models for Overture Maps features."""

from pydantic import BaseModel, Field

from overture.schema.validation.types import CountryCode, RegionCode

from .base import ExtensibleBaseModel


class AddressLevel(BaseModel):
    """Address level with optional value."""

    value: str | None = Field(None, description="Address level value")


class AddressContainer(ExtensibleBaseModel):
    """Address container with flexible admin levels."""

    freeform: str | None = Field(None, description="Freeform address string")
    locality: str | None = Field(None, description="Locality name")
    postcode: str | None = Field(None, description="Postal code")
    region: RegionCode | None = Field(None, description="ISO 3166-2 subdivision code")
    country: CountryCode | None = Field(
        None, description="ISO 3166-1 alpha-2 country code"
    )
    address_levels: list[AddressLevel] | None = Field(
        None, min_length=1, max_length=5, description="Address levels (1-5)"
    )
    postal_city: str | None = Field(None, description="Postal city if different")
