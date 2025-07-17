"""Scoping base classes for conditional rule application in Overture Maps features."""

from typing import Annotated, Literal

from pydantic import BaseModel, Field

from overture.schema.validation import MinItemsConstraint
from overture.schema.validation.types import LinearReferenceRange

from .base import ExtensibleBaseModel
from .transportation import (
    PurposeOfUse,
    RecognizedStatus,
    TravelMode,
    VehicleConstraint,
)


class GeometricRangeScope(ExtensibleBaseModel):
    """Base class for geometric range scoping using linear referencing.

    Enables rules to apply to specific portions of a linear feature by specifying
    start and end positions along the feature's geometry. This is the foundation
    for all spatially-scoped rules in the Overture Maps transportation schema.

    Examples:
        Simple geometric scoping with dimension values:
        ```python
        # For dimension values, use a simple structure:
        # Dimension = {"value": float, "unit": str}

        class WidthRule(GeometricRangeScope):
            width: dict[str, str | float]  # {"value": 3.5, "unit": "m"}
        ```

        Usage in YAML:
        ```yaml
        width_rules:
          - between: [0, 0.5]     # First half of segment
            width: {value: 3.5, unit: m}
          - between: [0.5, 1]     # Second half of segment
            width: {value: 2.8, unit: m}
        ```
    """

    between: LinearReferenceRange | None = Field(
        None,
        description="Linear referencing range [start, end] where 0=start, 1=end of feature",
    )


class TemporalScope(BaseModel):
    """Base class for temporal scoping using OSM opening hours format.

    Enables rules to apply during specific time periods, days of week, or date ranges.
    Uses the standardized OpenStreetMap opening hours specification for maximum
    compatibility and expressiveness.

    Examples:
        Rush hour speed limits:
        ```yaml
        speed_limits:
          - max_speed: {value: 30, unit: km/h}
            when:
              during: "Mo-Fr 07:00-09:00,17:00-19:00"
        ```

        Weekend parking restrictions:
        ```yaml
        access_restrictions:
          - access_type: denied
            when:
              during: "Sa-Su"
        ```

    See: https://wiki.openstreetmap.org/wiki/Key:opening_hours
    """

    during: str | None = Field(
        None,
        description="Time periods in OSM opening hours format (e.g., 'Mo-Fr 08:00-17:00')",
    )


class HeadingScope(BaseModel):
    """Base class for directional scoping based on travel direction.

    Enables rules to apply differently depending on the direction of travel
    along a linear feature. Essential for modeling asymmetric traffic rules
    like one-way restrictions or direction-specific speed limits.

    Examples:
        Direction-specific access:
        ```yaml
        access_restrictions:
          - access_type: denied
            when:
              heading: backward  # No travel against direction
        ```

        Lane-specific speed limits:
        ```yaml
        speed_limits:
          - max_speed: {value: 80, unit: km/h}
            when:
              heading: forward   # Faster speed in main direction
        ```
    """

    heading: Literal["forward", "backward"] | None = Field(
        None,
        description="Direction of travel: 'forward' follows feature geometry, 'backward' opposes it",
    )


class TravelModeScope(BaseModel):
    """Base class for travel mode scoping by transportation method.

    Enables rules to apply only to specific modes of transportation,
    allowing fine-grained control over who is affected by restrictions,
    speed limits, or other regulations.

    Examples:
        Bus-only restrictions:
        ```yaml
        access_restrictions:
          - access_type: denied
            when:
              mode: [bus]
        ```

        Multi-modal speed limits:
        ```yaml
        speed_limits:
          - max_speed: {value: 15, unit: km/h}
            when:
              mode: [foot, bike]  # Shared path speed limit
        ```
    """

    mode: Annotated[list[TravelMode], MinItemsConstraint(1)] | None = Field(
        None,
        description="Transportation modes affected by this rule (car, foot, bike, etc.)",
    )


class PurposeOfUseScope(BaseModel):
    """Base class for purpose of use scoping by travel intent.

    Enables rules to apply based on why someone is using the transportation
    network, allowing for nuanced restrictions that consider the purpose
    of travel rather than just the mode or vehicle type.

    Examples:
        Delivery-only access:
        ```yaml
        access_restrictions:
          - access_type: allowed
            when:
              using: [to_deliver]
        ```

        Destination access exemption:
        ```yaml
        access_restrictions:
          - access_type: denied
            when:
              using: [for_through_traffic]  # Block through traffic only
        ```
    """

    using: Annotated[list[PurposeOfUse], MinItemsConstraint(1)] | None = Field(
        None,
        description="Purpose of travel (to_deliver, at_destination, for_through_traffic, etc.)",
    )


class RecognizedStatusScope(BaseModel):
    """Base class for recognized status scoping by legal/social recognition.

    Enables rules to apply based on how a person or vehicle is recognized
    by authorities or property owners, allowing for role-based access control
    and privilege-based restrictions.

    Examples:
        Employee parking:
        ```yaml
        access_restrictions:
          - access_type: allowed
            when:
              recognized: [as_employee]
        ```

        Private property restrictions:
        ```yaml
        access_restrictions:
          - access_type: denied
            when:
              recognized: [as_public]  # Public excluded from private area
        ```
    """

    recognized: Annotated[list[RecognizedStatus], MinItemsConstraint(1)] | None = Field(
        None,
        description="Legal or social recognition status (as_private, as_employee, as_public, etc.)",
    )


class VehicleScope(BaseModel):
    """Base class for vehicle attribute scoping by physical characteristics.

    Enables rules to apply based on specific vehicle dimensions, weight,
    or other physical attributes. Essential for modeling bridge weight limits,
    height restrictions, and similar infrastructure constraints.

    Examples:
        Weight restrictions:
        ```yaml
        access_restrictions:
          - access_type: denied
            when:
              vehicle:
                - dimension: weight
                  comparison: greater_than
                  value: 7.5
                  unit: t
        ```

        Multi-dimensional constraints:
        ```yaml
        access_restrictions:
          - access_type: denied
            when:
              vehicle:
                - dimension: height
                  comparison: greater_than
                  value: 3.8
                  unit: m
                - dimension: length
                  comparison: greater_than
                  value: 12
                  unit: m
        ```
    """

    vehicle: Annotated[list[VehicleConstraint], MinItemsConstraint(1)] | None = Field(
        None,
        description="Physical vehicle constraints (weight, height, width, length limits)",
    )


class ScopingConditions(
    TemporalScope,
    HeadingScope,
    TravelModeScope,
    PurposeOfUseScope,
    RecognizedStatusScope,
    VehicleScope,
):
    """Combined scoping conditions providing comprehensive conditional rule application.

    Inherits from all individual scope containers to enable complex multi-dimensional
    scoping. Used as the foundation for sophisticated transportation rules that need
    to consider multiple factors simultaneously.

    This class serves as both a complete scoping solution and a reference implementation
    showing how individual scope containers can be composed together.

    Examples:
        Complex access restriction:
        ```yaml
        access_restrictions:
          - access_type: denied
            when:
              mode: [car]
              during: "Mo-Fr 15:00-18:00"  # Rush hour
              heading: forward              # One direction
              using: [for_through_traffic]  # Through traffic only
              vehicle:
                - dimension: weight
                  comparison: greater_than
                  value: 3.5
                  unit: t
        ```

        Multi-dimensional speed limit:
        ```yaml
        speed_limits:
          - max_speed: {value: 30, unit: km/h}
            when:
              mode: [car, truck]
              during: "Sa-Su"
              recognized: [as_public]
        ```

    Design Pattern:
        Rule-specific when clauses typically inherit from a subset of individual
        scope classes rather than using this complete implementation:

        ```python
        class SpeedLimitWhenClause(
            TemporalScope,
            HeadingScope,
            TravelModeScope,
            VehicleScope
        ):
            pass  # Excludes purpose and status for speed limits
        ```
    """

    pass
