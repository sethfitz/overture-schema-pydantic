"""Common type definitions using constraint-based validation."""

from typing import Annotated

from .constraints import (
    CategoryPatternConstraint,
    ConfidenceScoreConstraint,
    CountryCodeConstraint,
    HexColorConstraint,
    ISO8601DateTimeConstraint,
    JSONPointerConstraint,
    LanguageTagConstraint,
    LinearReferenceRangeConstraint,
    LiteralValueConstraint,
    NonNegativeConstraint,
    NoWhitespaceConstraint,
    PhoneNumberConstraint,
    RegionCodeConstraint,
    WhitespaceConstraint,
    WikidataConstraint,
    ZoomLevelConstraint,
)

# String types with constraints
LanguageTag = Annotated[str, LanguageTagConstraint()]
CountryCode = Annotated[str, CountryCodeConstraint()]
RegionCode = Annotated[str, RegionCodeConstraint()]
ISO8601DateTime = Annotated[str, ISO8601DateTimeConstraint()]
JSONPointer = Annotated[str, JSONPointerConstraint()]
TrimmedString = Annotated[str, WhitespaceConstraint()]
CategoryPattern = Annotated[str, CategoryPatternConstraint()]
PhoneNumber = Annotated[str, PhoneNumberConstraint()]
WikidataId = Annotated[str, WikidataConstraint()]
HexColor = Annotated[str, HexColorConstraint()]
NoWhitespaceString = Annotated[str, NoWhitespaceConstraint()]

# Numeric types with constraints
ConfidenceScore = Annotated[float, ConfidenceScoreConstraint()]
ZoomLevel = Annotated[int, ZoomLevelConstraint()]
NonNegativeFloat = Annotated[float, NonNegativeConstraint()]
NonNegativeInt = Annotated[int, NonNegativeConstraint()]

# Collection types with constraints
LinearReferenceRange = Annotated[list[float], LinearReferenceRangeConstraint()]


# Theme/type validation aliases
def theme_literal(theme_name: str) -> type:
    """Create a theme literal constraint type."""
    return Annotated[str, LiteralValueConstraint(theme_name, "theme")]


def type_literal(type_name: str) -> type:
    """Create a type literal constraint type."""
    return Annotated[str, LiteralValueConstraint(type_name, "type")]


# Commonly used dictionary types
LanguageNameMap = dict[LanguageTag, str]
