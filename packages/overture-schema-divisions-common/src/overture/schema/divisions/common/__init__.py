"""Common divisions structures and enums."""

from .models import (
    AreaBoundaryClass,
    CapitalOfDivisionItem,
    CountryCode,
    DivisionClass,
    DivisionSubtype,
    HierarchyItem,
    Norms,
    PerspectiveMode,
    Perspectives,
    PlaceType,
    Side,
)
from .validation import (
    parent_division_required_unless,
)

__all__ = [
    "PlaceType",
    "DivisionClass",
    "AreaBoundaryClass",
    "CapitalOfDivisionItem",
    "PerspectiveMode",
    "Side",
    "Perspectives",
    "HierarchyItem",
    "Norms",
    "CountryCode",
    "DivisionSubtype",
    "parent_division_required_unless",
]
