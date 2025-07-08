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
