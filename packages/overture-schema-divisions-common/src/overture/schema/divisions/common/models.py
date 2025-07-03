"""Common divisions theme structures and enums."""

import re
from enum import Enum
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field, field_validator

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
    countries: Annotated[List[CountryCode], UniqueItemsConstraint()] = Field(
        ..., min_length=1, description="ISO 3166-1 alpha-2 country codes"
    )


class HierarchyItem(BaseModel):
    """Single item in administrative hierarchy."""

    division_id: str = Field(..., description="Division identifier")
    subtype: PlaceType = Field(..., description="Administrative level")
    name: str = Field(..., description="Division name")


class Norms(BaseModel):
    """Local norms and standards."""

    driving_side: Optional[Side] = Field(
        None, description="Driving side (inheritable from parent)"
    )


class CountryCode(str):
    """ISO 3166-1 alpha-2 country code type."""

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


class DivisionSubtype(str, Enum):
    """Division feature subtypes."""

    DIVISION = "division"
    DIVISION_AREA = "division_area"
    DIVISION_BOUNDARY = "division_boundary"
