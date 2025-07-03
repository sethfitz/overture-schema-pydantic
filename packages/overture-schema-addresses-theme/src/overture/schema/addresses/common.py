"""Common addresses theme structures and utilities."""

import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class AddressLevel(BaseModel):
    """Single administrative level in address hierarchy."""

    value: Optional[str] = Field(
        None,
        pattern=r"^(\S.*)?\S$",
        min_length=1,
        description="Administrative level value (no leading/trailing whitespace)",
    )


class CountryCode(str):
    """ISO 3166-1 alpha-2 country code for addresses."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError("Country code must be a string")

        pattern = re.compile(r"^[A-Z]{2}$")
        if not pattern.match(v):
            raise ValueError(f"Invalid country code format: {v}")

        return cls(v)


class AddressComponent(BaseModel):
    """Base class for address components with whitespace validation."""

    @field_validator("*", mode="before")
    @classmethod
    def validate_no_whitespace_padding(cls, v):
        """Validate that string fields don't have leading/trailing whitespace."""
        if isinstance(v, str):
            # Check for leading/trailing whitespace
            if v != v.strip():
                raise ValueError(f"'{v}' has leading or trailing whitespace")

            # Validate pattern for non-empty strings
            if v and not re.match(r"^(\S.*)?\S$", v):
                raise ValueError(f"'{v}' does not match pattern '^(\\S.*)?\\S$'")

        return v
