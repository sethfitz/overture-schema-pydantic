"""Constraint-based validation for Overture Maps schemas."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections.abc import Collection
from typing import Any, get_origin

from pydantic import (
    BaseModel,
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
    ValidationError,
    ValidationInfo,
)
from pydantic_core import InitErrorDetails, core_schema


class BaseConstraint(ABC):
    """Base class for all constraints."""

    @abstractmethod
    def validate(self, value: Any, info: ValidationInfo) -> None:
        """Validate the value and raise ValidationError if invalid."""
        pass

    @abstractmethod
    def __get_pydantic_core_schema__(
        self, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """Generate Pydantic core schema."""
        pass

    def __get_pydantic_json_schema__(
        self, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        """Generate JSON schema. Override in subclasses for custom schema."""
        return handler(core_schema)


class StringConstraint(BaseConstraint):
    """Base class for string-based constraints."""

    def __get_pydantic_core_schema__(
        self, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        python_schema = handler(str)

        def validate_string(value: str, info: ValidationInfo) -> str:
            self.validate(value, info)
            return value

        return core_schema.with_info_after_validator_function(
            validate_string, python_schema
        )


class CollectionConstraint(BaseConstraint):
    """Base class for collection-based constraints."""

    def __get_pydantic_core_schema__(
        self, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        # Let the handler generate the proper schema for the collection type
        python_schema = handler(source)

        def validate_collection(value: Any, info: ValidationInfo) -> Any:
            self.validate(value, info)
            return value

        return core_schema.with_info_after_validator_function(
            validate_collection, python_schema
        )

    @staticmethod
    def _is_collection_type(source: type[Any]) -> bool:
        origin = get_origin(source)
        if origin is not None:
            return issubclass(origin, Collection)
        else:
            return issubclass(source, Collection)


class PatternConstraint(StringConstraint):
    """Generic pattern-based string constraint."""

    def __init__(self, pattern: str, error_message: str, flags: int = 0):
        self.pattern = re.compile(pattern, flags)
        self.pattern_str = pattern
        self.error_message = error_message

    def validate(self, value: str, info: ValidationInfo) -> None:
        if not self.pattern.match(value):
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("value",)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={"error": self.error_message.format(value=value)},
                    )
                ],
            )

    def __get_pydantic_json_schema__(
        self, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        json_schema = handler(core_schema)
        json_schema["pattern"] = self.pattern_str
        return json_schema


class LanguageTagConstraint(StringConstraint):
    """IETF BCP-47 language tag constraint."""

    def __init__(self, allow_private_use: bool = True):
        self.allow_private_use = allow_private_use
        # More permissive BCP-47 validation to handle various valid formats
        self.pattern = re.compile(
            r"^[a-z]{2,3}(-[A-Za-z]{2,8})*(-[0-9][A-Za-z0-9]{3})*$"
        )

    def validate(self, value: str, info: ValidationInfo) -> None:
        if not self.pattern.match(value):
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("value",)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={"error": f"Invalid IETF BCP-47 language tag: {value}"},
                    )
                ],
            )

    def __get_pydantic_json_schema__(
        self, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        json_schema = handler(core_schema)
        json_schema["pattern"] = self.pattern.pattern
        json_schema["description"] = "IETF BCP-47 language tag"
        return json_schema


class CountryCodeConstraint(StringConstraint):
    """ISO 3166-1 alpha-2 country code constraint."""

    def __init__(self):
        self.pattern = re.compile(r"^[A-Z]{2}$")

    def validate(self, value: str, info: ValidationInfo) -> None:
        if not self.pattern.match(value):
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("value",)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={
                            "error": f"Invalid ISO 3166-1 alpha-2 country code: {value}"
                        },
                    )
                ],
            )

    def __get_pydantic_json_schema__(
        self, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        json_schema = handler(core_schema)
        json_schema["pattern"] = self.pattern.pattern
        json_schema["description"] = "ISO 3166-1 alpha-2 country code"
        return json_schema


class RegionCodeConstraint(StringConstraint):
    """ISO 3166-2 subdivision code constraint."""

    def __init__(self):
        self.pattern = re.compile(r"^[A-Z]{2}-[A-Z0-9]{1,3}$")

    def validate(self, value: str, info: ValidationInfo) -> None:
        if not self.pattern.match(value):
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("value",)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={"error": f"Invalid ISO 3166-2 subdivision code: {value}"},
                    )
                ],
            )

    def __get_pydantic_json_schema__(
        self, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        json_schema = handler(core_schema)
        json_schema["pattern"] = self.pattern.pattern
        json_schema["description"] = "ISO 3166-2 subdivision code"
        return json_schema


class ISO8601DateTimeConstraint(StringConstraint):
    """ISO 8601 datetime constraint."""

    def __init__(self):
        # Simplified ISO 8601 validation
        self.pattern = re.compile(
            r"^([1-9]\d{3})-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])T"
            r"([01]\d|2[0-3]):([0-5]\d):([0-5]\d|60)(\.\d{1,3})?"
            r"(Z|[-+]([01]\d|2[0-3]):[0-5]\d)$"
        )

    def validate(self, value: str, info: ValidationInfo) -> None:
        if not self.pattern.match(value):
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("value",)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={"error": f"Invalid ISO 8601 datetime: {value}"},
                    )
                ],
            )

    def __get_pydantic_json_schema__(
        self, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        json_schema = handler(core_schema)
        json_schema["format"] = "date-time"
        json_schema["description"] = "ISO 8601 datetime"
        return json_schema


class JSONPointerConstraint(StringConstraint):
    """JSON Pointer constraint (RFC 6901)."""

    def validate(self, value: str, info: ValidationInfo) -> None:
        # Empty string represents root pointer
        if value == "":
            return

        if not value.startswith("/"):
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("value",)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={
                            "error": f"JSON Pointer must start with '/' or be empty string: {value}"
                        },
                    )
                ],
            )

    def __get_pydantic_json_schema__(
        self, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        json_schema = handler(core_schema)
        json_schema["description"] = "JSON Pointer (RFC 6901)"
        return json_schema


class LinearReferenceRangeConstraint(CollectionConstraint):
    """Linear reference range constraint (0.0 to 1.0)."""

    def validate(self, value: list[float], info: ValidationInfo) -> None:
        if len(value) != 2:
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("value",)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={
                            "error": f"Linear reference range must have exactly 2 values, got {len(value)}"
                        },
                    )
                ],
            )

        start, end = value
        if not (0.0 <= start <= 1.0 and 0.0 <= end <= 1.0):
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("value",)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={
                            "error": f"Linear reference range values must be between 0.0 and 1.0: [{start}, {end}]"
                        },
                    )
                ],
            )

        if start >= end:
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("value",)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={
                            "error": f"Linear reference range start must be less than end: [{start}, {end}]"
                        },
                    )
                ],
            )

    def __get_pydantic_json_schema__(
        self, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        json_schema = handler(core_schema)
        json_schema["type"] = "array"
        json_schema["minItems"] = 2
        json_schema["maxItems"] = 2
        json_schema["items"] = {"type": "number", "minimum": 0.0, "maximum": 1.0}
        json_schema["description"] = (
            "Linear reference range [start, end] where 0.0 <= start < end <= 1.0"
        )
        return json_schema


class MinItemsConstraint(CollectionConstraint):
    """Minimum items constraint for collections."""

    def __init__(self, min_items: int):
        if not isinstance(min_items, int):
            raise ValueError(
                f"min_items must be an int, got {type(min_items).__name__}"
            )
        if min_items < 1:
            raise ValueError(f"min_items must be positive, got {min_items}")
        self.min_items = min_items

    def validate(self, value: Any, info: ValidationInfo) -> None:
        num_items = len(value)
        if num_items < self.min_items:
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("value",)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={
                            "error": f"Collection has too few items: expected len>={self.min_items} but got len={num_items}"
                        },
                    )
                ],
            )

    def __get_pydantic_json_schema__(
        self, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        json_schema = handler(core_schema)
        schema_type = json_schema.get("type")
        if schema_type == "array":
            json_schema["minItems"] = self.min_items
        elif schema_type == "object":
            json_schema["minProperties"] = self.min_items
        return json_schema


class MaxItemsConstraint(CollectionConstraint):
    """Maximum items constraint for collections."""

    def __init__(self, max_items: int):
        if not isinstance(max_items, int):
            raise ValueError(
                f"max_items must be an int, got {type(max_items).__name__}"
            )
        if max_items < 1:
            raise ValueError(f"max_items must be positive, got {max_items}")
        self.max_items = max_items

    def validate(self, value: Any, info: ValidationInfo) -> None:
        num_items = len(value)
        if num_items > self.max_items:
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("value",)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={
                            "error": f"Collection has too many items: expected len<={self.max_items} but got len={num_items}"
                        },
                    )
                ],
            )

    def __get_pydantic_json_schema__(
        self, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        json_schema = handler(core_schema)
        schema_type = json_schema.get("type")
        if schema_type == "array":
            json_schema["maxItems"] = self.max_items
        elif schema_type == "object":
            json_schema["maxProperties"] = self.max_items
        return json_schema


class WhitespaceConstraint(StringConstraint):
    """Constraint to ensure string has no leading/trailing whitespace."""

    def validate(self, value: str, info: ValidationInfo) -> None:
        if value != value.strip():
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("value",)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={
                            "error": f"String cannot have leading or trailing whitespace: {repr(value)}"
                        },
                    )
                ],
            )


class UniqueItemsConstraint(CollectionConstraint):
    """Constraint to ensure all items in a collection are unique."""

    def validate(self, value: list[Any], info: ValidationInfo) -> None:
        if len(value) != len(set(value)):
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("value",)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={"error": "All items must be unique"},
                    )
                ],
            )

    def __get_pydantic_json_schema__(
        self, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        json_schema = handler(core_schema)
        json_schema["uniqueItems"] = True
        return json_schema


class CategoryPatternConstraint(StringConstraint):
    """Constraint for place category patterns (snake_case)."""

    def __init__(self):
        self.pattern = re.compile(r"^[a-z0-9]+(_[a-z0-9]+)*$")

    def validate(self, value: str, info: ValidationInfo) -> None:
        if not self.pattern.match(value):
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("value",)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={
                            "error": f"Invalid category format: {value}. Must be snake_case (lowercase letters, numbers, underscores)"
                        },
                    )
                ],
            )

    def __get_pydantic_json_schema__(
        self, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        json_schema = handler(core_schema)
        json_schema["pattern"] = self.pattern.pattern
        json_schema["description"] = "Category in snake_case format"
        return json_schema


class WikidataConstraint(StringConstraint):
    """Constraint for Wikidata identifiers (Q followed by digits)."""

    def __init__(self):
        self.pattern = re.compile(r"^Q\d+$")

    def validate(self, value: str, info: ValidationInfo) -> None:
        if not self.pattern.match(value):
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("value",)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={
                            "error": f"Invalid Wikidata identifier: {value}. Must be Q followed by digits (e.g., Q123)"
                        },
                    )
                ],
            )

    def __get_pydantic_json_schema__(
        self, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        json_schema = handler(core_schema)
        json_schema["pattern"] = self.pattern.pattern
        json_schema["description"] = "Wikidata identifier (Q followed by digits)"
        return json_schema


class PhoneNumberConstraint(StringConstraint):
    """Constraint for international phone numbers."""

    def __init__(self):
        self.pattern = re.compile(r"^\+\d{1,3}[\s\-\(\)0-9]+$")

    def validate(self, value: str, info: ValidationInfo) -> None:
        if not self.pattern.match(value):
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("value",)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={
                            "error": f"Invalid phone number format: {value}. Must start with + and country code"
                        },
                    )
                ],
            )

    def __get_pydantic_json_schema__(
        self, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        json_schema = handler(core_schema)
        json_schema["pattern"] = self.pattern.pattern
        json_schema["description"] = (
            "International phone number (+ followed by country code and number)"
        )
        return json_schema


class ConfidenceScoreConstraint(BaseConstraint):
    """Constraint for confidence/probability scores (0.0 to 1.0)."""

    def validate(self, value: float, info: ValidationInfo) -> None:
        if not (0.0 <= value <= 1.0):
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("value",)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={
                            "error": f"Confidence score must be between 0.0 and 1.0, got {value}"
                        },
                    )
                ],
            )

    def __get_pydantic_core_schema__(
        self, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        python_schema = handler(float)

        def validate_confidence(value: float, info: ValidationInfo) -> float:
            self.validate(value, info)
            return value

        return core_schema.with_info_after_validator_function(
            validate_confidence, python_schema
        )

    def __get_pydantic_json_schema__(
        self, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        json_schema = handler(core_schema)
        json_schema["minimum"] = 0.0
        json_schema["maximum"] = 1.0
        json_schema["description"] = "Confidence score between 0.0 and 1.0"
        return json_schema


class ZoomLevelConstraint(BaseConstraint):
    """Constraint for map zoom levels (0 to 23)."""

    def validate(self, value: int, info: ValidationInfo) -> None:
        if not (0 <= value <= 23):
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("value",)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={
                            "error": f"Zoom level must be between 0 and 23, got {value}"
                        },
                    )
                ],
            )

    def __get_pydantic_core_schema__(
        self, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        python_schema = handler(int)

        def validate_zoom(value: int, info: ValidationInfo) -> int:
            self.validate(value, info)
            return value

        return core_schema.with_info_after_validator_function(
            validate_zoom, python_schema
        )

    def __get_pydantic_json_schema__(
        self, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        json_schema = handler(core_schema)
        json_schema["minimum"] = 0
        json_schema["maximum"] = 23
        json_schema["description"] = "Map zoom level between 0 and 23"
        return json_schema


class NonNegativeConstraint(BaseConstraint):
    """Constraint for non-negative numbers."""

    def validate(self, value: int | float, info: ValidationInfo) -> None:
        if value < 0:
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("value",)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={"error": f"Value must be non-negative, got {value}"},
                    )
                ],
            )

    def __get_pydantic_core_schema__(
        self, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        python_schema = handler(source)

        def validate_non_negative(
            value: int | float, info: ValidationInfo
        ) -> int | float:
            self.validate(value, info)
            return value

        return core_schema.with_info_after_validator_function(
            validate_non_negative, python_schema
        )

    def __get_pydantic_json_schema__(
        self, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        json_schema = handler(core_schema)
        json_schema["minimum"] = 0
        json_schema["description"] = "Non-negative number"
        return json_schema


class LiteralValueConstraint(BaseConstraint):
    """Constraint for literal value validation (e.g., theme must be 'places')."""

    def __init__(self, expected_value: Any, field_name: str = "value"):
        self.expected_value = expected_value
        self.field_name = field_name

    def validate(self, value: Any, info: ValidationInfo) -> None:
        if value != self.expected_value:
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("value",)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={
                            "error": f"{self.field_name} must be '{self.expected_value}', got '{value}'"
                        },
                    )
                ],
            )

    def __get_pydantic_core_schema__(
        self, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        python_schema = handler(source)

        def validate_literal(value: Any, info: ValidationInfo) -> Any:
            self.validate(value, info)
            return value

        return core_schema.with_info_after_validator_function(
            validate_literal, python_schema
        )

    def __get_pydantic_json_schema__(
        self, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        json_schema = handler(core_schema)
        json_schema["const"] = self.expected_value
        json_schema["description"] = f"Must be exactly '{self.expected_value}'"
        return json_schema


class HexColorConstraint(StringConstraint):
    """Constraint for hexadecimal color codes (e.g., #FF0000)."""

    def __init__(self):
        self.pattern = re.compile(r"^#[0-9A-Fa-f]{6}$")

    def validate(self, value: str, info: ValidationInfo) -> None:
        if not self.pattern.match(value):
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("value",)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={
                            "error": f"Invalid hexadecimal color format: {value}. Must be in format #RRGGBB (e.g., #FF0000)"
                        },
                    )
                ],
            )

    def __get_pydantic_json_schema__(
        self, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        json_schema = handler(core_schema)
        json_schema["pattern"] = self.pattern.pattern
        json_schema["description"] = "Hexadecimal color code in format #RRGGBB"
        return json_schema


class NoWhitespaceConstraint(StringConstraint):
    """Constraint for strings that cannot contain whitespace characters."""

    def __init__(self):
        self.pattern = re.compile(r"^\S+$")

    def validate(self, value: str, info: ValidationInfo) -> None:
        if not self.pattern.match(value):
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("value",)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={
                            "error": f"String cannot contain whitespace characters: '{value}'"
                        },
                    )
                ],
            )

    def __get_pydantic_json_schema__(
        self, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        json_schema = handler(core_schema)
        json_schema["pattern"] = self.pattern.pattern
        json_schema["description"] = "String without whitespace characters"
        return json_schema


class CompositeUniqueConstraint(CollectionConstraint):
    """Constraint for composite uniqueness validation using attribute extraction."""

    def __init__(self, *attribute_paths: str):
        """Initialize with attribute paths to extract for uniqueness comparison.

        Args:
            *attribute_paths: Attribute names or paths to extract from each item
                             for uniqueness comparison (e.g., 'value', 'type')
        """
        if not attribute_paths:
            raise ValueError("At least one attribute path must be specified")
        self.attribute_paths = attribute_paths

    def validate(self, value: list[Any], info: ValidationInfo) -> None:
        """Validate that items are unique based on composite attribute values."""
        composite_keys = []

        for item in value:
            # Extract attribute values to create composite key
            key_parts = []
            for attr_path in self.attribute_paths:
                if hasattr(item, attr_path):
                    key_parts.append(getattr(item, attr_path))
                elif isinstance(item, dict) and attr_path in item:
                    key_parts.append(item[attr_path])
                else:
                    # If attribute doesn't exist, use None as part of key
                    key_parts.append(None)

            composite_keys.append(tuple(key_parts))

        # Check for duplicates
        if len(composite_keys) != len(set(composite_keys)):
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("value",)

            # Find the duplicated keys for better error message
            seen = set()
            duplicates = set()
            for key in composite_keys:
                if key in seen:
                    duplicates.add(key)
                seen.add(key)

            attr_names = ", ".join(self.attribute_paths)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={
                            "error": f"Items must be unique based on ({attr_names}). Found duplicates: {list(duplicates)}"
                        },
                    )
                ],
            )

    def __get_pydantic_json_schema__(
        self, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        json_schema = handler(core_schema)
        json_schema["uniqueItems"] = True
        attr_names = ", ".join(self.attribute_paths)
        json_schema["description"] = f"Items must be unique based on ({attr_names})"
        return json_schema


class ConditionalRequiredConstraint(BaseConstraint):
    """Constraint for conditional field requirements based on other field values."""

    def __init__(
        self, condition_field: str, condition_value: Any, required_fields: list[str]
    ):
        """Initialize conditional requirement constraint.

        Args:
            condition_field: Field name to check condition against
            condition_value: Value that triggers the requirement
            required_fields: List of field names that become required
        """
        self.condition_field = condition_field
        self.condition_value = condition_value
        self.required_fields = required_fields

    def validate(self, value: BaseModel, info: ValidationInfo) -> None:
        """Validate conditional requirements on a model."""
        if not isinstance(value, BaseModel):
            return

        # Check if condition is met
        if hasattr(value, self.condition_field):
            condition_field_value = getattr(value, self.condition_field)
            if condition_field_value == self.condition_value:
                # Check if required fields are present and not None
                for field_name in self.required_fields:
                    if (
                        not hasattr(value, field_name)
                        or getattr(value, field_name) is None
                    ):
                        context = info.context or {}
                        loc = context.get("loc_prefix", ()) + (field_name,)
                        raise ValidationError.from_exception_data(
                            title=self.__class__.__name__,
                            line_errors=[
                                InitErrorDetails(
                                    type="value_error",
                                    loc=loc,
                                    input=value,
                                    ctx={
                                        "error": f"Field '{field_name}' is required when '{self.condition_field}' is '{self.condition_value}'"
                                    },
                                )
                            ],
                        )

    def __get_pydantic_core_schema__(
        self, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        if not issubclass(source, BaseModel):
            raise TypeError(
                f"{type(self).__name__} can only be applied to BaseModel subclasses; "
                f"but it was applied to {source.__name__}"
            )
        schema = handler(source)

        def validator_wrapper(value: Any, info: ValidationInfo) -> Any:
            self.validate(value, info)
            return value

        return core_schema.with_info_after_validator_function(validator_wrapper, schema)


class MutuallyExclusiveConstraint(BaseConstraint):
    """Constraint for mutually exclusive boolean fields."""

    def __init__(self, *field_names: str):
        """Initialize mutually exclusive constraint.

        Args:
            *field_names: Names of fields that cannot all be true simultaneously
        """
        if len(field_names) < 2:
            raise ValueError("At least two field names must be specified")
        self.field_names = field_names

    def validate(self, value: BaseModel, info: ValidationInfo) -> None:
        """Validate that at most one of the specified boolean fields is true."""
        if not isinstance(value, BaseModel):
            return

        true_fields = []
        for field_name in self.field_names:
            if hasattr(value, field_name):
                field_value = getattr(value, field_name)
                if field_value is True:
                    true_fields.append(field_name)

        if len(true_fields) > 1:
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + tuple(true_fields)
            field_list = ", ".join(true_fields)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={
                            "error": f"Fields {field_list} are mutually exclusive and cannot all be true"
                        },
                    )
                ],
            )

    def __get_pydantic_core_schema__(
        self, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        if not issubclass(source, BaseModel):
            raise TypeError(
                f"{type(self).__name__} can only be applied to BaseModel subclasses; "
                f"but it was applied to {source.__name__}"
            )
        schema = handler(source)

        def validator_wrapper(value: Any, info: ValidationInfo) -> Any:
            self.validate(value, info)
            return value

        return core_schema.with_info_after_validator_function(validator_wrapper, schema)


class AtLeastOneOfConstraint(BaseConstraint):
    """Constraint ensuring at least one of specified fields is present and not None."""

    def __init__(self, *field_names: str):
        """Initialize at-least-one-of constraint.

        Args:
            *field_names: Names of fields where at least one must be present
        """
        if len(field_names) < 2:
            raise ValueError("At least two field names must be specified")
        self.field_names = field_names

    def validate(self, value: BaseModel, info: ValidationInfo) -> None:
        """Validate that at least one of the specified fields is present and not None."""
        if not isinstance(value, BaseModel):
            return

        present_fields = []
        for field_name in self.field_names:
            if hasattr(value, field_name):
                field_value = getattr(value, field_name)
                if field_value is not None:
                    present_fields.append(field_name)

        if not present_fields:
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("__root__",)
            field_list = ", ".join(self.field_names)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={
                            "error": f"At least one of these fields must be present: {field_list}"
                        },
                    )
                ],
            )

    def __get_pydantic_core_schema__(
        self, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        if not issubclass(source, BaseModel):
            raise TypeError(
                f"{type(self).__name__} can only be applied to BaseModel subclasses; "
                f"but it was applied to {source.__name__}"
            )
        schema = handler(source)

        def validator_wrapper(value: Any, info: ValidationInfo) -> Any:
            self.validate(value, info)
            return value

        return core_schema.with_info_after_validator_function(validator_wrapper, schema)


class ThemeTypeCompatibilityConstraint(BaseConstraint):
    """Constraint to validate that theme and type combination is compatible."""

    def __init__(self, compatibility_check_func):
        """Initialize with a function to check theme-type compatibility."""
        self.compatibility_check_func = compatibility_check_func

    def validate(self, value: BaseModel, info: ValidationInfo) -> None:
        """Validate that theme and type are compatible."""
        if not isinstance(value, BaseModel):
            return

        if hasattr(value, "theme") and hasattr(value, "type"):
            theme = value.theme
            feature_type = value.type

            if not self.compatibility_check_func(theme, feature_type):
                context = info.context or {}
                loc = context.get("loc_prefix", ()) + ("type",)
                raise ValidationError.from_exception_data(
                    title=self.__class__.__name__,
                    line_errors=[
                        InitErrorDetails(
                            type="value_error",
                            loc=loc,
                            input=value,
                            ctx={
                                "error": f"Invalid theme-type combination: theme='{theme}', type='{feature_type}'. "
                                f"Type '{feature_type}' is not valid for theme '{theme}'"
                            },
                        )
                    ],
                )

    def __get_pydantic_core_schema__(
        self, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        if not issubclass(source, BaseModel):
            raise TypeError(
                f"{type(self).__name__} can only be applied to BaseModel subclasses; "
                f"but it was applied to {source.__name__}"
            )
        schema = handler(source)

        def validator_wrapper(value: Any, info: ValidationInfo) -> Any:
            self.validate(value, info)
            return value

        return core_schema.with_info_after_validator_function(validator_wrapper, schema)


class CountryRequiredConstraint(BaseConstraint):
    """Constraint requiring country field for specific subtypes."""

    def __init__(
        self, excluded_subtype, subtype_field="subtype", country_field="country"
    ):
        """Initialize constraint.

        Args:
            excluded_subtype: Subtype value that doesn't require country
            subtype_field: Name of the subtype field
            country_field: Name of the country field
        """
        self.excluded_subtype = excluded_subtype
        self.subtype_field = subtype_field
        self.country_field = country_field

    def validate(self, value: BaseModel, info: ValidationInfo) -> None:
        """Validate that country is present unless subtype is excluded."""
        if not isinstance(value, BaseModel):
            return

        if hasattr(value, self.subtype_field) and hasattr(value, self.country_field):
            subtype = getattr(value, self.subtype_field)
            country = getattr(value, self.country_field)

            if country is None and subtype != self.excluded_subtype:
                context = info.context or {}
                loc = context.get("loc_prefix", ()) + (self.country_field,)
                raise ValidationError.from_exception_data(
                    title=self.__class__.__name__,
                    line_errors=[
                        InitErrorDetails(
                            type="value_error",
                            loc=loc,
                            input=value,
                            ctx={
                                "error": f"Field '{self.country_field}' is required when '{self.subtype_field}' is not '{self.excluded_subtype}'"
                            },
                        )
                    ],
                )

    def __get_pydantic_core_schema__(
        self, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        if not issubclass(source, BaseModel):
            raise TypeError(
                f"{type(self).__name__} can only be applied to BaseModel subclasses; "
                f"but it was applied to {source.__name__}"
            )
        schema = handler(source)

        def validator_wrapper(value: Any, info: ValidationInfo) -> Any:
            self.validate(value, info)
            return value

        return core_schema.with_info_after_validator_function(validator_wrapper, schema)


class GeometryTypeConstraint(BaseConstraint):
    """Constraint for validating GeoJSON geometry types using Shapely."""

    def __init__(self, allowed_types: list[str]):
        """Initialize with allowed geometry types.

        Args:
            allowed_types: List of allowed GeoJSON geometry types (e.g., ["Point", "Polygon"])
        """
        # Validate allowed types at constraint creation
        self._geometry_types = (
            "GeometryCollection",
            "LineString",
            "Point",
            "Polygon",
            "MultiLineString",
            "MultiPoint",
            "MultiPolygon",
        )

        if not allowed_types:
            raise ValueError(
                f"allowed_types is empty (it must contain at least one of: {self._geometry_types})"
            )

        if not all(item in self._geometry_types for item in allowed_types):
            invalid = [
                item for item in allowed_types if item not in self._geometry_types
            ]
            raise ValueError(
                f"allowed_types contains invalid values: {invalid} (allowed: {self._geometry_types})"
            )

        self.allowed_types = tuple(sorted(allowed_types))

    def validate(self, value: dict[str, Any], info: ValidationInfo) -> None:
        """Validate GeoJSON geometry type and structure."""
        if not isinstance(value, dict):
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("value",)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={"error": "Geometry must be an object"},
                    )
                ],
            )

        geometry_type = value.get("type")
        if not geometry_type:
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("type",)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={"error": "Geometry must have a 'type' property"},
                    )
                ],
            )

        if geometry_type not in self._geometry_types:
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("type",)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={
                            "error": f"Invalid geometry type '{geometry_type}' (allowed: {self._geometry_types})"
                        },
                    )
                ],
            )

        if geometry_type not in self.allowed_types:
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("type",)
            allowed_list = ", ".join(self.allowed_types)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={
                            "error": f"Geometry type '{geometry_type}' not allowed (allowed: [{allowed_list}])"
                        },
                    )
                ],
            )

        # Validate geometry structure using Shapely
        try:
            from shapely.errors import ShapelyError
            from shapely.geometry import shape

            # This will validate the GeoJSON structure and coordinates
            shape(value)
        except (ShapelyError, ValueError, TypeError) as e:
            context = info.context or {}
            loc = context.get("loc_prefix", ()) + ("value",)
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=loc,
                        input=value,
                        ctx={"error": f"Invalid geometry structure: {str(e)}"},
                    )
                ],
            ) from e

    def __get_pydantic_core_schema__(
        self, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        python_schema = handler(source)

        def validate_geometry(
            value: dict[str, Any], info: ValidationInfo
        ) -> dict[str, Any]:
            self.validate(value, info)
            return value

        return core_schema.with_info_after_validator_function(
            validate_geometry, python_schema
        )

    def __get_pydantic_json_schema__(
        self, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        json_schema = handler(core_schema)
        json_schema["properties"] = json_schema.get("properties", {})
        json_schema["properties"]["type"] = {
            "type": "string",
            "enum": list(self.allowed_types),
        }
        json_schema["description"] = (
            f"GeoJSON geometry with type one of: {', '.join(self.allowed_types)}"
        )
        return json_schema
