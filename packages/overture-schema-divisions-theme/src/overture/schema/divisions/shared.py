"""Common divisions theme structures and enums."""

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field

from overture.schema.validation import CountryCode, UniqueItemsConstraint


class PlaceType(str, Enum):
    """Administrative hierarchy levels for divisions."""

    COUNTRY = "country"
    DEPENDENCY = "dependency"
    MACROREGION = "macroregion"
    REGION = "region"
    MACROCOUNTY = "macrocounty"
    COUNTY = "county"
    LOCALADMIN = "localadmin"
    LOCALITY = "locality"
    BOROUGH = "borough"
    MACROHOOD = "macrohood"
    NEIGHBORHOOD = "neighborhood"
    MICROHOOD = "microhood"


class DivisionClass(str, Enum):
    """Division-specific class designations."""

    MEGACITY = "megacity"
    CITY = "city"
    TOWN = "town"
    VILLAGE = "village"
    HAMLET = "hamlet"


class AreaBoundaryClass(str, Enum):
    """Area and boundary class designations."""

    LAND = "land"
    MARITIME = "maritime"


class PerspectiveMode(str, Enum):
    """Political perspective validation modes."""

    ACCEPTED_BY = "accepted_by"
    DISPUTED_BY = "disputed_by"


class Side(str, Enum):
    """Driving side for norms."""

    LEFT = "left"
    RIGHT = "right"


class Perspectives(BaseModel):
    """Political perspectives container."""

    mode: PerspectiveMode = Field(..., description="Perspective validation mode")
    countries: Annotated[list[CountryCode], UniqueItemsConstraint()] = Field(
        ..., min_length=1, description="ISO 3166-1 alpha-2 country codes"
    )


class HierarchyItem(BaseModel):
    """Single item in administrative hierarchy."""

    division_id: str = Field(..., description="Division identifier")
    subtype: PlaceType = Field(..., description="Administrative level")
    name: str = Field(..., description="Division name")

    def __hash__(self) -> int:
        """Make HierarchyItem hashable for uniqueness constraints."""
        return hash((self.division_id, self.subtype, self.name))

    def __eq__(self, other) -> bool:
        """Equality comparison for HierarchyItem."""
        if not isinstance(other, HierarchyItem):
            return False
        return (
            self.division_id == other.division_id
            and self.subtype == other.subtype
            and self.name == other.name
        )


class CapitalOfDivisionItem(BaseModel):
    """Division that has this division as capital."""

    division_id: str = Field(..., description="Division identifier")
    subtype: PlaceType = Field(..., description="Administrative level")

    def __hash__(self) -> int:
        """Make CapitalOfDivisionItem hashable for uniqueness constraints."""
        return hash((self.division_id, self.subtype))

    def __eq__(self, other) -> bool:
        """Equality comparison for CapitalOfDivisionItem."""
        if not isinstance(other, CapitalOfDivisionItem):
            return False
        return self.division_id == other.division_id and self.subtype == other.subtype


class Norms(BaseModel):
    """Local norms and standards."""

    driving_side: Side | None = Field(
        None, description="Driving side (inheritable from parent)"
    )


class DivisionSubtype(str, Enum):
    """Division feature subtypes."""

    DIVISION = "division"
    DIVISION_AREA = "division_area"
    DIVISION_BOUNDARY = "division_boundary"
