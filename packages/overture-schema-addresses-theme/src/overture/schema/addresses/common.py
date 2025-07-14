"""Common addresses theme structures and utilities."""

from typing import Annotated, Optional

from pydantic import BaseModel, Field

from overture.schema.validation.constraints import WhitespaceConstraint


class AddressLevel(BaseModel):
    """Single administrative level in address hierarchy."""

    value: Optional[Annotated[str, WhitespaceConstraint()]] = Field(
        None,
        min_length=1,
        description="Administrative level value (no leading/trailing whitespace)",
    )
