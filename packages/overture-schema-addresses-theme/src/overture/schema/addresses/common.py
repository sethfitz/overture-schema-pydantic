"""Common addresses theme structures and utilities."""

from typing import Annotated

from pydantic import BaseModel, Field

from overture.schema.validation.constraints import WhitespaceConstraint


class AddressLevel(BaseModel):
    """Single administrative level in address hierarchy."""

    value: Annotated[str, WhitespaceConstraint()] | None = Field(
        None,
        min_length=1,
        description="Administrative level value (no leading/trailing whitespace)",
    )
