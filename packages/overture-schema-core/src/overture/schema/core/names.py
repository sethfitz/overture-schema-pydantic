"""Name-related models for Overture Maps features."""

from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from overture.schema.validation import MinItemsConstraint
from overture.schema.validation.types import (
    CountryCode,
    LanguageTag,
    LinearReferenceRange,
    TrimmedString,
)

from .base import ExtensibleBaseModel


class NameVariant(str, Enum):
    """Name variant types."""

    COMMON = "common"
    OFFICIAL = "official"
    ALTERNATE = "alternate"
    SHORT = "short"


class PerspectiveMode(str, Enum):
    """Perspective mode for disputed names."""

    ACCEPTED_BY = "accepted_by"
    DISPUTED_BY = "disputed_by"


class NamePerspectives(BaseModel):
    """Political perspectives for names."""

    mode: PerspectiveMode = Field(..., description="Perspective mode")
    countries: Annotated[list[CountryCode], MinItemsConstraint(1)] = Field(
        ..., description="ISO 3166-1 alpha-2 country codes"
    )


class NameRule(BaseModel):
    """Name rule with variant and language specification."""

    variant: NameVariant = Field(..., description="Name variant type")
    value: TrimmedString = Field(..., min_length=1, description="Name value")
    language: LanguageTag | None = Field(None, description="IETF BCP-47 language tag")
    perspectives: NamePerspectives | None = Field(
        None, description="Political perspectives"
    )
    between: LinearReferenceRange | None = Field(
        None, description="Linear referencing range"
    )
    side: Literal["left", "right"] | None = Field(
        None, description="Side specification"
    )


class NamesContainer(ExtensibleBaseModel):
    """Multilingual names container."""

    primary: TrimmedString = Field(..., min_length=1, description="Primary name")
    common: dict[LanguageTag, TrimmedString] | None = Field(
        None, description="Common names by language"
    )
    rules: list[NameRule] | None = Field(None, description="Name rules")
