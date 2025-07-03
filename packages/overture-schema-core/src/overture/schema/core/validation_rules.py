"""Generic validation rule system for Overture Maps features."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Set, Tuple


class ValidationRuleType(str, Enum):
    """Types of validation rules."""

    ENUM_VALUES = "enum_values"
    UNIQUE_ARRAY = "unique_array"
    DISALLOWED_PROPERTY = "disallowed_property"
    REQUIRED_PROPERTY = "required_property"
    DATA_TYPE = "data_type"
    REFERENCE_FORMAT = "reference_format"
    LINEAR_REFERENCE = "linear_reference"
    CONDITIONAL_PROPERTY = "conditional_property"


class ValidationRule(ABC):
    """Base class for validation rules that work cleanly with Pydantic."""

    def __init__(self, field_path: str = "", error_message: str = ""):
        self.field_path = field_path
        self.error_message = error_message

    @abstractmethod
    def __call__(self, feature: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate the rule against a feature."""
        pass

    def get_field_value(self, feature: Dict[str, Any], path: str) -> Any:
        """Get value at field path, supporting nested access."""
        try:
            current = feature
            for part in path.split("."):
                if part.startswith("[") and part.endswith("]"):
                    # Array index access
                    index = int(part[1:-1])
                    current = current[index]
                else:
                    current = current[part]
            return current
        except (KeyError, IndexError, TypeError):
            return None

    def __and__(self, other: "ValidationRule") -> "ValidationRule":
        """Combine rules with AND logic: both must pass."""
        return _AndRule(self, other)

    def __or__(self, other: "ValidationRule") -> "ValidationRule":
        """Combine rules with OR logic: at least one must pass."""
        return _OrRule(self, other)

    def __invert__(self) -> "ValidationRule":
        """Negate rule: must fail for this to pass."""
        return _NotRule(self)


class EnumValidationRule(ValidationRule):
    """Validate that field values are from allowed sets."""

    def __init__(
        self, field_path: str, allowed_values: Set[str], error_message: str = ""
    ):
        super().__init__(field_path, error_message)
        self.allowed_values = allowed_values

    def __call__(self, feature: Dict[str, Any]) -> Tuple[bool, str]:
        value = self.get_field_value(feature, self.field_path)
        if value is None:
            return True, ""  # Optional field

        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict) and "values" in item:
                    # Handle road_flags structure: [{"values": ["flag1", "flag2"]}]
                    for flag in item["values"]:
                        if flag not in self.allowed_values:
                            return (
                                False,
                                self.error_message
                                or f"Invalid value '{flag}' at {self.field_path}",
                            )
                elif item not in self.allowed_values:
                    return (
                        False,
                        self.error_message
                        or f"Invalid value '{item}' at {self.field_path}",
                    )
        elif value not in self.allowed_values:
            return (
                False,
                self.error_message or f"Invalid value '{value}' at {self.field_path}",
            )

        return True, ""


class UniqueArrayRule(ValidationRule):
    """Validate that array values are unique."""

    def __init__(self, field_path: str, error_message: str = ""):
        super().__init__(field_path, error_message)

    def __call__(self, feature: Dict[str, Any]) -> Tuple[bool, str]:
        value = self.get_field_value(feature, self.field_path)
        if value is None:
            return True, ""  # Optional field

        if isinstance(value, list):
            if isinstance(value[0], dict) and "values" in value[0]:
                # Handle road_flags structure: [{"values": ["flag1", "flag2"]}]
                for item in value:
                    if "values" in item:
                        flags = item["values"]
                        if len(flags) != len(set(flags)):
                            return (
                                False,
                                self.error_message
                                or f"Duplicate values found in {self.field_path}",
                            )
            else:
                # Regular array
                if len(value) != len(set(value)):
                    return (
                        False,
                        self.error_message
                        or f"Duplicate values found in {self.field_path}",
                    )

        return True, ""


class DisallowedPropertyRule(ValidationRule):
    """Validate that certain properties don't exist."""

    def __init__(self, property_name: str, error_message: str = ""):
        super().__init__(property_name, error_message)
        self.property_name = property_name

    def __call__(self, feature: Dict[str, Any]) -> Tuple[bool, str]:
        properties = feature.get("properties", {})
        if self.property_name in properties:
            return (
                False,
                self.error_message or f"Property '{self.property_name}' is not allowed",
            )
        return True, ""


class UnrecognizedPropertyRule(ValidationRule):
    """Validate that only recognized properties or ext_ prefixed properties exist."""

    def __init__(self, allowed_properties: Set[str], error_message: str = ""):
        super().__init__("properties", error_message)
        self.allowed_properties = allowed_properties

    def __call__(self, feature: Dict[str, Any]) -> Tuple[bool, str]:
        properties = feature.get("properties", {})
        for prop_name in properties.keys():
            if prop_name not in self.allowed_properties and not prop_name.startswith(
                "ext_"
            ):
                return (
                    False,
                    self.error_message or f"Unrecognized property '{prop_name}'",
                )
        return True, ""


class DataTypeRule(ValidationRule):
    """Validate that fields have correct data types."""

    def __init__(self, field_path: str, expected_type: type, error_message: str = ""):
        super().__init__(field_path, error_message)
        self.expected_type = expected_type

    def __call__(self, feature: Dict[str, Any]) -> Tuple[bool, str]:
        value = self.get_field_value(feature, self.field_path)
        if value is None:
            return True, ""  # Optional field

        if not isinstance(value, self.expected_type):
            return (
                False,
                self.error_message
                or f"Field {self.field_path} must be {self.expected_type.__name__}",
            )

        return True, ""


class LinearReferenceRule(ValidationRule):
    """Validate linear referencing ranges."""

    def __call__(self, feature: Dict[str, Any]) -> Tuple[bool, str]:
        value = self.get_field_value(feature, self.field_path)
        if value is None:
            return True, ""  # Optional field

        if not isinstance(value, list) or len(value) != 2:
            return (
                False,
                f"Linear reference range must be array of 2 values at {self.field_path}",
            )

        start, end = value
        if not (isinstance(start, (int, float)) and isinstance(end, (int, float))):
            return (
                False,
                f"Linear reference values must be numbers at {self.field_path}",
            )

        if not (0.0 <= start <= 1.0 and 0.0 <= end <= 1.0):
            return (
                False,
                f"Linear reference values must be between 0.0 and 1.0 at {self.field_path}",
            )

        if start >= end:
            return (
                False,
                f"Linear reference start must be less than end at {self.field_path}",
            )

        return True, ""


class NamesValidationRule(ValidationRule):
    """Validate names structure with rules."""

    VALID_VARIANTS = {"common", "official", "alternate", "short"}

    def __call__(self, feature: Dict[str, Any]) -> Tuple[bool, str]:
        properties = feature.get("properties", {})
        names = properties.get("names")

        if names is None:
            return True, ""  # Optional field

        if not isinstance(names, dict):
            return False, "names must be an object"

        # Validate rules array if present
        rules = names.get("rules")
        if rules is not None:
            if not isinstance(rules, list):
                return False, "names.rules must be an array"

            for i, rule in enumerate(rules):
                if not isinstance(rule, dict):
                    return False, f"names.rules[{i}] must be an object"

                # Variant is required in rules
                if "variant" not in rule:
                    return (
                        False,
                        f"names.rules[{i}] missing required property 'variant'",
                    )

                variant = rule["variant"]
                if variant not in self.VALID_VARIANTS:
                    return (
                        False,
                        f"names.rules[{i}].variant must be one of {list(self.VALID_VARIANTS)}, got '{variant}'",
                    )

                # Value is required in rules
                if "value" not in rule:
                    return False, f"names.rules[{i}] missing required property 'value'"

        return True, ""


class RoadFlagsStructureRule(ValidationRule):
    """Validate road_flags structure - must be array of objects with values property."""

    def __call__(self, feature: Dict[str, Any]) -> Tuple[bool, str]:
        properties = feature.get("properties", {})
        road_flags = properties.get("road_flags")

        if road_flags is None:
            return True, ""  # Optional field

        if not isinstance(road_flags, list):
            return False, "road_flags must be an array"

        for i, flag_item in enumerate(road_flags):
            if not isinstance(flag_item, dict):
                return (
                    False,
                    f"road_flags[{i}] must be an object, got {type(flag_item).__name__}",
                )

            if "values" not in flag_item:
                return False, f"road_flags[{i}] missing required property 'values'"

            values = flag_item["values"]
            if not isinstance(values, list):
                return False, f"road_flags[{i}].values must be an array"

        return True, ""


class RequiredPropertyRule(ValidationRule):
    """Validate that required properties exist."""

    def __init__(self, property_name: str, error_message: str = ""):
        super().__init__(property_name, error_message)
        self.property_name = property_name

    def __call__(self, feature: Dict[str, Any]) -> Tuple[bool, str]:
        # Handle nested property paths like "properties.version"
        if self.property_name.startswith("properties."):
            prop_name = self.property_name[11:]  # Remove "properties." prefix
            properties = feature.get("properties", {})
            if prop_name not in properties:
                return (
                    False,
                    self.error_message or f"Required property '{prop_name}' is missing",
                )
        else:
            # Direct property access
            if self.property_name not in feature:
                return (
                    False,
                    self.error_message
                    or f"Required property '{self.property_name}' is missing",
                )
        return True, ""


class DiscriminatedUnionRule(ValidationRule):
    """Validate discriminated unions based on a discriminator field."""

    def __init__(
        self,
        discriminator_field: str,
        union_schemas: Dict[str, List[ValidationRule]],
        error_message: str = "",
    ):
        super().__init__(discriminator_field, error_message)
        self.discriminator_field = discriminator_field
        self.union_schemas = union_schemas

    def __call__(self, feature: Dict[str, Any]) -> Tuple[bool, str]:
        discriminator_value = self.get_field_value(feature, self.discriminator_field)
        if discriminator_value is None:
            return False, f"Missing discriminator field '{self.discriminator_field}'"

        if discriminator_value not in self.union_schemas:
            return (
                False,
                f"Unknown discriminator value '{discriminator_value}' for field '{self.discriminator_field}'",
            )

        # Validate against the specific schema for this discriminator value
        schema_rules = self.union_schemas[discriminator_value]
        for rule in schema_rules:
            is_valid, error_msg = rule(feature)
            if not is_valid:
                return False, error_msg

        return True, ""


class OneOfRule(ValidationRule):
    """Validate that exactly one of the provided schemas matches."""

    def __init__(self, schemas: List[List[ValidationRule]], error_message: str = ""):
        super().__init__("", error_message)
        self.schemas = schemas

    def __call__(self, feature: Dict[str, Any]) -> Tuple[bool, str]:
        pass_count = 0

        for schema_rules in self.schemas:
            schema_valid = True
            for rule in schema_rules:
                is_valid, _ = rule(feature)
                if not is_valid:
                    schema_valid = False
                    break

            if schema_valid:
                pass_count += 1

        if pass_count == 0:
            return (
                False,
                self.error_message or "Failed to match any of the required conditions",
            )
        elif pass_count > 1:
            return (
                False,
                self.error_message
                or "More than one condition matched, but exactly one is required",
            )

        return True, ""


class AnyOfRule(ValidationRule):
    """Validate that at least one of the provided schemas matches."""

    def __init__(self, schemas: List[List[ValidationRule]], error_message: str = ""):
        super().__init__("", error_message)
        self.schemas = schemas

    def __call__(self, feature: Dict[str, Any]) -> Tuple[bool, str]:
        for schema_rules in self.schemas:
            schema_valid = True
            for rule in schema_rules:
                is_valid, _ = rule(feature)
                if not is_valid:
                    schema_valid = False
                    break

            if schema_valid:
                return True, ""

        return (
            False,
            self.error_message or "Failed to match any of the required conditions",
        )


class ExtensibleObjectRule(ValidationRule):
    """Validate extensible objects with known keys and extension prefix."""

    def __init__(
        self,
        field_path: str,
        known_keys: Set[str],
        extension_prefix: str = "ext_",
        error_message: str = "",
    ):
        super().__init__(field_path, error_message)
        self.known_keys = known_keys
        self.extension_prefix = extension_prefix

    def __call__(self, feature: Dict[str, Any]) -> Tuple[bool, str]:
        value = self.get_field_value(feature, self.field_path)
        if value is None:
            return True, ""  # Optional field

        if not isinstance(value, dict):
            return False, f"Field {self.field_path} must be an object"

        unrecognized_keys = []
        for key in value.keys():
            if key not in self.known_keys and not key.startswith(self.extension_prefix):
                unrecognized_keys.append(key)

        if unrecognized_keys:
            return (
                False,
                self.error_message
                or f"Unrecognized keys in {self.field_path}: {', '.join(unrecognized_keys)}",
            )

        return True, ""


class AscendingRangeRule(ValidationRule):
    """Validate that a range has values in ascending order."""

    def __init__(self, field_path: str, error_message: str = ""):
        super().__init__(field_path, error_message)

    def __call__(self, feature: Dict[str, Any]) -> Tuple[bool, str]:
        value = self.get_field_value(feature, self.field_path)
        if value is None:
            return True, ""  # Optional field

        if not isinstance(value, list) or len(value) != 2:
            return False, f"Field {self.field_path} must be an array with 2 elements"

        start, end = value
        if not (isinstance(start, (int, float)) and isinstance(end, (int, float))):
            return False, f"Range values in {self.field_path} must be numbers"

        if start >= end:
            return (
                False,
                self.error_message
                or f"Range values in {self.field_path} must be in ascending order",
            )

        return True, ""


class ConditionalRequiredRule(ValidationRule):
    """Validate that a field is required when a condition is met."""

    def __init__(
        self,
        field_path: str,
        condition_field: str,
        condition_value: Any,
        error_message: str = "",
    ):
        super().__init__(field_path, error_message)
        self.condition_field = condition_field
        self.condition_value = condition_value

    def __call__(self, feature: Dict[str, Any]) -> Tuple[bool, str]:
        condition_actual = self.get_field_value(feature, self.condition_field)

        if condition_actual == self.condition_value:
            field_value = self.get_field_value(feature, self.field_path)
            if field_value is None:
                return (
                    False,
                    self.error_message
                    or f"Field {self.field_path} is required when {self.condition_field} is {self.condition_value}",
                )

        return True, ""


class _AndRule(ValidationRule):
    """Combines two rules with AND logic."""

    def __init__(self, left: ValidationRule, right: ValidationRule):
        super().__init__("", "")
        self.left = left
        self.right = right

    def __call__(self, feature: Dict[str, Any]) -> Tuple[bool, str]:
        is_valid_left, error_left = self.left(feature)
        if not is_valid_left:
            return False, error_left

        is_valid_right, error_right = self.right(feature)
        if not is_valid_right:
            return False, error_right

        return True, ""


class _OrRule(ValidationRule):
    """Combines two rules with OR logic."""

    def __init__(self, left: ValidationRule, right: ValidationRule):
        super().__init__("", "")
        self.left = left
        self.right = right

    def __call__(self, feature: Dict[str, Any]) -> Tuple[bool, str]:
        is_valid_left, error_left = self.left(feature)
        if is_valid_left:
            return True, ""

        is_valid_right, error_right = self.right(feature)
        if is_valid_right:
            return True, ""

        return False, f"Both conditions failed: ({error_left}) and ({error_right})"


class _NotRule(ValidationRule):
    """Negates a rule."""

    def __init__(self, rule: ValidationRule):
        super().__init__("", "")
        self.rule = rule

    def __call__(self, feature: Dict[str, Any]) -> Tuple[bool, str]:
        is_valid, _ = self.rule(feature)
        if is_valid:
            return False, "Rule should have failed but passed"
        return True, ""


# Registry for validation rules by theme and type
_VALIDATION_RULES: Dict[Tuple[str, str], List[ValidationRule]] = {}


def register_validation_rules(
    theme: str, feature_type: str, rules: List[ValidationRule]
) -> None:
    """Register validation rules for a theme/type combination."""
    key = (theme, feature_type)
    if key not in _VALIDATION_RULES:
        _VALIDATION_RULES[key] = []
    _VALIDATION_RULES[key].extend(rules)


def validate_with_rules(
    theme: str, feature_type: str, feature: Dict[str, Any]
) -> Tuple[bool, str]:
    """Validate a feature against registered rules."""
    key = (theme, feature_type)
    if key not in _VALIDATION_RULES:
        return True, ""  # No rules registered

    rules = _VALIDATION_RULES[key]
    for rule in rules:
        is_valid, error_msg = rule(feature)
        if not is_valid:
            return False, error_msg

    return True, ""


def get_registered_rules(theme: str = None, feature_type: str = None) -> Dict[str, Any]:
    """Get information about registered validation rules for reflection."""
    if theme and feature_type:
        key = (theme, feature_type)
        if key not in _VALIDATION_RULES:
            return {}

        rules_info = []
        for rule in _VALIDATION_RULES[key]:
            rule_info = {
                "type": rule.rule_type,
                "field_path": rule.field_path,
                "error_message": rule.error_message,
                "metadata": rule.metadata,
            }
            rules_info.append(rule_info)

        return {"theme": theme, "feature_type": feature_type, "rules": rules_info}

    # Return all rules grouped by theme/type
    all_rules = {}
    for (theme_key, type_key), rules in _VALIDATION_RULES.items():
        if theme_key not in all_rules:
            all_rules[theme_key] = {}

        rules_info = []
        for rule in rules:
            rule_info = {
                "type": rule.rule_type,
                "field_path": rule.field_path,
                "error_message": rule.error_message,
                "metadata": rule.metadata,
            }
            rules_info.append(rule_info)

        all_rules[theme_key][type_key] = rules_info

    return all_rules


def create_rule_from_config(config: Dict[str, Any]) -> ValidationRule:
    """Create a validation rule from configuration for code generation."""
    rule_type = config.get("type")

    if rule_type == "EnumValidationRule":
        return EnumValidationRule(
            config["field_path"],
            set(config["allowed_values"]),
            config.get("error_message", ""),
        )
    elif rule_type == "UniqueArrayRule":
        return UniqueArrayRule(config["field_path"], config.get("error_message", ""))
    elif rule_type == "ExtensibleObjectRule":
        return ExtensibleObjectRule(
            config["field_path"],
            set(config["known_keys"]),
            config.get("extension_prefix", "ext_"),
            config.get("error_message", ""),
        )
    elif rule_type == "DiscriminatedUnionRule":
        # Recursively create union schemas
        union_schemas = {}
        for discriminator_value, schema_config in config["union_schemas"].items():
            union_schemas[discriminator_value] = [
                create_rule_from_config(rule_config) for rule_config in schema_config
            ]
        return DiscriminatedUnionRule(
            config["discriminator_field"],
            union_schemas,
            config.get("error_message", ""),
        )
    elif rule_type == "ConditionalRequiredRule":
        return ConditionalRequiredRule(
            config["field_path"],
            config["condition_field"],
            config["condition_value"],
            config.get("error_message", ""),
        )
    else:
        raise ValueError(f"Unknown rule type: {rule_type}")


# Predefined rule sets for common validation patterns

# Transportation road flags
VALID_ROAD_FLAGS = {
    "is_bridge",
    "is_tunnel",
    "is_covered",
    "is_indoor",
    "is_private",
    "is_abandoned",
    "is_under_construction",
    "is_toll",
    "is_link",
}

# Transportation travel modes
VALID_TRAVEL_MODES = {
    "car",
    "foot",
    "bike",
    "hgv",
    "bus",
    "taxi",
    "motorcycle",
    "emergency",
    "delivery",
    "vehicle",
    "motor_vehicle",
    "truck",
    "bicycle",
    "hov",
}

# Division subtypes
VALID_DIVISION_SUBTYPES = {
    "country",
    "dependency",
    "region",
    "county",
    "locality",
    "neighborhood",
}

# Building classes
VALID_BUILDING_CLASSES = {
    "agricultural",
    "civic",
    "commercial",
    "education",
    "entertainment",
    "industrial",
    "medical",
    "military",
    "office",
    "residential",
    "religious",
    "service",
    "transportation",
    "utility",
}
