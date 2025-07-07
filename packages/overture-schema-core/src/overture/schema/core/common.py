"""Common container structures for Overture Maps features."""

from enum import Enum
from typing import Annotated, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from overture.schema.validation import (
    MinItemsConstraint,
)
from overture.schema.validation.types import (
    CountryCode,
    ISO8601DateTime,
    JSONPointer,
    LanguageTag,
    LinearReferenceRange,
    RegionCode,
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
    countries: Annotated[List[CountryCode], MinItemsConstraint(1)] = Field(
        ..., description="ISO 3166-1 alpha-2 country codes"
    )


class NameRule(BaseModel):
    """Name rule with variant and language specification."""

    variant: NameVariant = Field(..., description="Name variant type")
    value: TrimmedString = Field(..., min_length=1, description="Name value")
    language: Optional[LanguageTag] = Field(
        None, description="IETF BCP-47 language tag"
    )
    perspectives: Optional[NamePerspectives] = Field(
        None, description="Political perspectives"
    )
    between: Optional[LinearReferenceRange] = Field(
        None, description="Linear referencing range"
    )
    side: Optional[Literal["left", "right"]] = Field(
        None, description="Side specification"
    )


class NamesContainer(ExtensibleBaseModel):
    """Multilingual names container."""

    primary: TrimmedString = Field(..., min_length=1, description="Primary name")
    common: Optional[Dict[LanguageTag, TrimmedString]] = Field(
        None, description="Common names by language"
    )
    rules: Optional[List[NameRule]] = Field(None, description="Name rules")


class LinearReferenceRangeContainer(BaseModel):
    """Linear reference range container for geometric scoping."""

    between: LinearReferenceRange = Field(..., description="Range between 0.0 and 1.0")


class AdvancedSourceItem(BaseModel):
    """Advanced source information with linear referencing support."""

    property: JSONPointer = Field(..., description="JSON Pointer to the property")
    dataset: str = Field(..., description="Source dataset identifier")
    record_id: Optional[str] = Field(None, description="Specific record within dataset")
    update_time: Optional[ISO8601DateTime] = Field(
        None, description="When this property was last updated (ISO 8601)"
    )
    confidence: Optional[float] = Field(
        None, ge=0, le=1, description="Confidence value for ML-derived data"
    )
    between: Optional[LinearReferenceRange] = Field(
        None, description="Linear referencing range"
    )


class AddressLevel(BaseModel):
    """Address level with optional value."""

    value: Optional[str] = Field(None, description="Address level value")


class AddressContainer(ExtensibleBaseModel):
    """Address container with flexible admin levels."""

    freeform: Optional[str] = Field(None, description="Freeform address string")
    locality: Optional[str] = Field(None, description="Locality name")
    postcode: Optional[str] = Field(None, description="Postal code")
    region: Optional[RegionCode] = Field(
        None, description="ISO 3166-2 subdivision code"
    )
    country: Optional[CountryCode] = Field(
        None, description="ISO 3166-1 alpha-2 country code"
    )
    address_levels: Optional[List[AddressLevel]] = Field(
        None, min_length=1, max_length=5, description="Address levels (1-5)"
    )
    postal_city: Optional[str] = Field(None, description="Postal city if different")


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

    between: Optional[LinearReferenceRange] = Field(
        None, description="Linear referencing range [start, end]"
    )


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

    mode: Optional[Annotated[List[TravelMode], MinItemsConstraint(1)]] = Field(
        None, description="Travel modes"
    )


class PurposeOfUseScopeContainer(BaseModel):
    """Base class for purpose of use scoping."""

    using: Optional[Annotated[List[PurposeOfUse], MinItemsConstraint(1)]] = Field(
        None, description="Purpose of use"
    )


class RecognizedStatusScopeContainer(BaseModel):
    """Base class for recognized status scoping."""

    recognized: Optional[Annotated[List[RecognizedStatus], MinItemsConstraint(1)]] = (
        Field(None, description="Recognized status")
    )


class VehicleScopeContainer(BaseModel):
    """Base class for vehicle attribute scoping."""

    vehicle: Optional[Annotated[List[VehicleConstraint], MinItemsConstraint(1)]] = (
        Field(None, description="Vehicle constraints")
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
