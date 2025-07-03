"""Common container structures for Overture Maps features."""

import re
from enum import Enum
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

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
    countries: List[str] = Field(
        ..., min_length=1, description="ISO 3166-1 alpha-2 country codes"
    )

    @field_validator("countries")
    @classmethod
    def validate_country_codes(cls, v):
        """Validate ISO 3166-1 alpha-2 country codes."""
        pattern = re.compile(r"^[A-Z]{2}$")
        for country in v:
            if not pattern.match(country):
                raise ValueError(f"Invalid country code: {country}")
        return v


class NameRule(BaseModel):
    """Name rule with variant and language specification."""

    variant: NameVariant = Field(..., description="Name variant type")
    value: str = Field(..., min_length=1, description="Name value")
    language: Optional[str] = Field(None, description="IETF BCP-47 language tag")
    perspectives: Optional[NamePerspectives] = Field(
        None, description="Political perspectives"
    )
    between: Optional[List[float]] = Field(None, description="Linear referencing range")
    side: Optional[str] = Field(None, description="Side specification")

    @field_validator("language")
    @classmethod
    def validate_language_tag(cls, v):
        """Validate IETF BCP-47 language tag."""
        if v is None:
            return v

        # More permissive BCP-47 validation to handle various valid formats
        # Including private use subtags and complex language variants
        pattern = re.compile(r"^[a-z]{2,3}(-[A-Za-z]{2,8})*(-[0-9][A-Za-z0-9]{3})*$")
        if not pattern.match(v):
            raise ValueError(f"Invalid language tag: {v}")
        return v

    @field_validator("between")
    @classmethod
    def validate_between_range(cls, v):
        """Validate linear referencing range."""
        if v is None:
            return v

        if len(v) != 2:
            raise ValueError("between must have exactly 2 values")

        start, end = v
        if not (0.0 <= start <= 1.0 and 0.0 <= end <= 1.0):
            raise ValueError("between values must be between 0.0 and 1.0")

        if start >= end:
            raise ValueError("between start must be less than end")

        return v

    @field_validator("side")
    @classmethod
    def validate_side(cls, v):
        """Validate side specification."""
        if v is not None and v not in ["left", "right"]:
            raise ValueError("side must be 'left' or 'right'")
        return v


class NamesContainer(ExtensibleBaseModel):
    """Multilingual names container."""

    primary: str = Field(..., min_length=1, description="Primary name")
    common: Optional[Dict[str, str]] = Field(
        None, description="Common names by language"
    )
    rules: Optional[List[NameRule]] = Field(None, description="Name rules")

    @field_validator("primary")
    @classmethod
    def validate_primary_whitespace(cls, v):
        """Validate primary name doesn't have leading/trailing whitespace."""
        if v != v.strip():
            raise ValueError("Primary name cannot have leading or trailing whitespace")
        return v

    @field_validator("common")
    @classmethod
    def validate_common_languages(cls, v):
        """Validate language tags in common names."""
        if v is None:
            return v

        # More permissive BCP-47 validation to handle various valid formats
        pattern = re.compile(r"^[a-z]{2,3}(-[A-Za-z]{2,8})*(-[0-9][A-Za-z0-9]{3})*$")

        for lang_tag, name in v.items():
            if not pattern.match(lang_tag):
                raise ValueError(f"Invalid language tag: {lang_tag}")
            if not name or name != name.strip():
                raise ValueError(f"Invalid name for language {lang_tag}")

        return v


class LinearReferenceRange(BaseModel):
    """Linear reference range for geometric scoping."""

    between: List[float] = Field(..., description="Range between 0.0 and 1.0")

    @field_validator("between")
    @classmethod
    def validate_range(cls, v):
        """Validate linear reference range."""
        if len(v) != 2:
            raise ValueError("between must have exactly 2 values")

        start, end = v
        if not (0.0 <= start <= 1.0 and 0.0 <= end <= 1.0):
            raise ValueError("between values must be between 0.0 and 1.0")

        if start >= end:
            raise ValueError("between start must be less than end")

        return v


class AdvancedSourceItem(BaseModel):
    """Advanced source information with linear referencing support."""

    property: str = Field(..., description="JSON Pointer to the property")
    dataset: str = Field(..., description="Source dataset identifier")
    record_id: Optional[str] = Field(None, description="Specific record within dataset")
    update_time: Optional[str] = Field(
        None, description="When this property was last updated (ISO 8601)"
    )
    confidence: Optional[float] = Field(
        None, ge=0, le=1, description="Confidence value for ML-derived data"
    )
    between: Optional[List[float]] = Field(None, description="Linear referencing range")

    @field_validator("property")
    @classmethod
    def validate_json_pointer(cls, v):
        """Validate JSON Pointer format."""
        # Empty string represents root pointer
        if v == "":
            return v
        if not v.startswith("/"):
            raise ValueError("JSON Pointer must start with '/' or be empty string")
        return v

    @field_validator("update_time")
    @classmethod
    def validate_iso_datetime(cls, v):
        """Validate ISO 8601 datetime format."""
        if v is None:
            return v

        # Simplified ISO 8601 validation
        pattern = re.compile(
            r"^([1-9]\d{3})-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])T"
            r"([01]\d|2[0-3]):([0-5]\d):([0-5]\d|60)(\.\d{1,3})?"
            r"(Z|[-+]([01]\d|2[0-3]):[0-5]\d)$"
        )
        if not pattern.match(v):
            raise ValueError(f"Invalid ISO 8601 datetime: {v}")
        return v

    @field_validator("between")
    @classmethod
    def validate_between_range(cls, v):
        """Validate linear referencing range."""
        if v is None:
            return v

        if len(v) != 2:
            raise ValueError("between must have exactly 2 values")

        start, end = v
        if not (0.0 <= start <= 1.0 and 0.0 <= end <= 1.0):
            raise ValueError("between values must be between 0.0 and 1.0")

        if start >= end:
            raise ValueError("between start must be less than end")

        return v


class AddressLevel(BaseModel):
    """Address level with optional value."""

    value: Optional[str] = Field(None, description="Address level value")


class AddressContainer(ExtensibleBaseModel):
    """Address container with flexible admin levels."""

    freeform: Optional[str] = Field(None, description="Freeform address string")
    locality: Optional[str] = Field(None, description="Locality name")
    postcode: Optional[str] = Field(None, description="Postal code")
    region: Optional[str] = Field(None, description="ISO 3166-2 subdivision code")
    country: Optional[str] = Field(None, description="ISO 3166-1 alpha-2 country code")
    address_levels: Optional[List[AddressLevel]] = Field(
        None, min_length=1, max_length=5, description="Address levels (1-5)"
    )
    postal_city: Optional[str] = Field(None, description="Postal city if different")

    @field_validator("country")
    @classmethod
    def validate_country_code(cls, v):
        """Validate ISO 3166-1 alpha-2 country code."""
        if v is None:
            return v

        pattern = re.compile(r"^[A-Z]{2}$")
        if not pattern.match(v):
            raise ValueError(f"Invalid country code: {v}")
        return v

    @field_validator("region")
    @classmethod
    def validate_region_code(cls, v):
        """Validate ISO 3166-2 subdivision code."""
        if v is None:
            return v

        pattern = re.compile(r"^[A-Z]{2}-[A-Z0-9]{1,3}$")
        if not pattern.match(v):
            raise ValueError(f"Invalid region code: {v}")
        return v


# Linear Referencing Types and Containers

LinearlyReferencedPosition = float
LinearlyReferencedRange = List[LinearlyReferencedPosition]


class TravelMode(str, Enum):
    """Travel mode enumeration."""

    CAR = "car"
    FOOT = "foot"
    BIKE = "bike"
    HGV = "hgv"
    BUS = "bus"
    TAXI = "taxi"
    MOTORCYCLE = "motorcycle"
    EMERGENCY = "emergency"
    DELIVERY = "delivery"
    VEHICLE = "vehicle"
    MOTOR_VEHICLE = "motor_vehicle"
    TRUCK = "truck"
    BICYCLE = "bicycle"
    HOV = "hov"


class VehicleDimension(str, Enum):
    """Vehicle dimension types."""

    WEIGHT = "weight"
    HEIGHT = "height"
    WIDTH = "width"
    LENGTH = "length"
    AXLE_LOAD = "axle_load"
    AXLE_COUNT = "axle_count"


class VehicleComparison(str, Enum):
    """Vehicle comparison operators."""

    EQUAL = "equal"
    NOT_EQUAL = "not_equal"
    LESS_THAN = "less_than"
    LESS_THAN_EQUAL = "less_than_equal"
    GREATER_THAN = "greater_than"
    GREATER_THAN_EQUAL = "greater_than_equal"


class PurposeOfUse(str, Enum):
    """Purpose of use enumeration."""

    TO_DELIVER = "to_deliver"
    AT_DESTINATION = "at_destination"
    THROUGH_TRAFFIC = "through_traffic"
    AS_CUSTOMER = "as_customer"
    TO_FARM = "to_farm"


class RecognizedStatus(str, Enum):
    """Recognized status enumeration."""

    AS_PRIVATE = "as_private"
    AS_EMPLOYEE = "as_employee"
    AS_CUSTOMER = "as_customer"
    AS_RESIDENT = "as_resident"
    AS_PERMITTED = "as_permitted"


class Speed(BaseModel):
    """Speed value with unit."""

    value: float = Field(..., gt=0, description="Speed value")
    unit: Literal["km/h", "mph"] = Field(..., description="Speed unit")


class Dimension(BaseModel):
    """Physical dimension with value and unit."""

    value: float = Field(..., gt=0, description="Dimension value")
    unit: str = Field(..., description="Dimension unit")


class VehicleConstraint(BaseModel):
    """Vehicle constraint specification."""

    dimension: VehicleDimension = Field(..., description="Vehicle dimension")
    comparison: VehicleComparison = Field(..., description="Comparison operator")
    value: float = Field(..., description="Constraint value")
    unit: Optional[str] = Field(None, description="Unit of measurement")


class GeometricRangeScopeContainer(ExtensibleBaseModel):
    """Base class for geometric range scoping."""

    between: Optional[LinearlyReferencedRange] = Field(
        None, description="Linear referencing range [start, end]"
    )

    @field_validator("between")
    @classmethod
    def validate_between_range(cls, v):
        """Validate linear referencing range."""
        if v is None:
            return v

        if len(v) != 2:
            raise ValueError("between must have exactly 2 values")

        start, end = v
        if not (0.0 <= start <= 1.0 and 0.0 <= end <= 1.0):
            raise ValueError("between values must be between 0.0 and 1.0")

        if start >= end:
            raise ValueError("between start must be less than end")

        return v


class TemporalScopeContainer(BaseModel):
    """Base class for temporal scoping."""

    during: Optional[str] = Field(None, description="OSM opening hours format")


class HeadingScopeContainer(BaseModel):
    """Base class for directional scoping."""

    heading: Optional[Literal["forward", "backward"]] = Field(
        None, description="Direction of travel"
    )


class TravelModeScopeContainer(BaseModel):
    """Base class for travel mode scoping."""

    mode: Optional[List[TravelMode]] = Field(
        None, min_length=1, description="Travel modes"
    )


class PurposeOfUseScopeContainer(BaseModel):
    """Base class for purpose of use scoping."""

    using: Optional[List[PurposeOfUse]] = Field(
        None, min_length=1, description="Purpose of use"
    )


class RecognizedStatusScopeContainer(BaseModel):
    """Base class for recognized status scoping."""

    recognized: Optional[List[RecognizedStatus]] = Field(
        None, min_length=1, description="Recognized status"
    )


class VehicleScopeContainer(BaseModel):
    """Base class for vehicle attribute scoping."""

    vehicle: Optional[List[VehicleConstraint]] = Field(
        None, min_length=1, description="Vehicle constraints"
    )


class ScopingConditions(
    TemporalScopeContainer,
    HeadingScopeContainer,
    TravelModeScopeContainer,
    PurposeOfUseScopeContainer,
    RecognizedStatusScopeContainer,
    VehicleScopeContainer,
):
    """Combined scoping conditions for complex rules."""

    pass
