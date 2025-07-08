"""
Mixin-based constraint validation system with decorators.

This module provides a structured approach to model-level validation with
proper JSON Schema generation.
"""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, model_validator

# Registry for storing constraint validators per model class
_constraint_registry: dict[str, list["BaseConstraintValidator"]] = {}


class BaseConstraintValidator(ABC):
    """Base class for constraint validators."""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    @abstractmethod
    def validate(self, model_instance: BaseModel) -> None:
        """Validate the constraint against the model instance."""
        pass

    @abstractmethod
    def get_json_schema_metadata(self) -> dict[str, Any]:
        """Return JSON Schema metadata for this constraint."""
        pass


class MutuallyExclusiveValidator(BaseConstraintValidator):
    """Validates mutually exclusive fields."""

    def __init__(self, *field_names: str):
        super().__init__()
        self.field_names = field_names

    def validate(self, model_instance: BaseModel) -> None:
        target = model_instance
        if hasattr(model_instance, "properties"):
            target = model_instance.properties

        true_fields = []
        for field_name in self.field_names:
            if hasattr(target, field_name) and getattr(target, field_name) is True:
                true_fields.append(field_name)

        if len(true_fields) > 1:
            raise ValueError(
                f"Fields {', '.join(true_fields)} are mutually exclusive and cannot all be true"
            )

    def get_json_schema_metadata(self) -> dict[str, Any]:
        return {
            "type": "mutually_exclusive",
            "fields": list(self.field_names),
            "not": {
                "allOf": [
                    {"properties": {field: {"const": True}}}
                    for field in self.field_names
                ]
            },
        }


class RequiredIfValidator(BaseConstraintValidator):
    """Validates conditional field requirements."""

    def __init__(
        self, condition_field: str, condition_value: Any, required_fields: list[str]
    ):
        super().__init__()
        self.condition_field = condition_field
        self.condition_value = condition_value
        self.required_fields = required_fields

    def validate(self, model_instance: BaseModel) -> None:
        target = model_instance
        if hasattr(model_instance, "properties"):
            target = model_instance.properties

        if hasattr(target, self.condition_field):
            condition_value = getattr(target, self.condition_field)
            if condition_value == self.condition_value:
                for field_name in self.required_fields:
                    if (
                        not hasattr(target, field_name)
                        or getattr(target, field_name) is None
                    ):
                        raise ValueError(
                            f"Field '{field_name}' is required when "
                            f"{self.condition_field} = {self.condition_value}"
                        )

    def get_json_schema_metadata(self) -> dict[str, Any]:
        return {
            "type": "required_if",
            "condition_field": self.condition_field,
            "condition_value": self.condition_value,
            "required_fields": self.required_fields,
            "if": {
                "properties": {self.condition_field: {"const": self.condition_value}}
            },
            "then": {"required": self.required_fields},
        }


class NotRequiredIfValidator(BaseConstraintValidator):
    """Validates conditional field NOT requirements (field should be None when condition is met)."""

    def __init__(
        self, condition_field: str, condition_value: Any, not_required_fields: list[str]
    ):
        super().__init__()
        self.condition_field = condition_field
        self.condition_value = condition_value
        self.not_required_fields = not_required_fields

    def validate(self, model_instance: BaseModel) -> None:
        target = model_instance
        if hasattr(model_instance, "properties"):
            target = model_instance.properties

        if hasattr(target, self.condition_field):
            condition_value = getattr(target, self.condition_field)
            if condition_value != self.condition_value:
                for field_name in self.not_required_fields:
                    if (
                        not hasattr(target, field_name)
                        or getattr(target, field_name) is None
                    ):
                        raise ValueError(
                            f"Field '{field_name}' is required when "
                            f"{self.condition_field} != {self.condition_value}"
                        )

    def get_json_schema_metadata(self) -> dict[str, Any]:
        return {
            "type": "not_required_if",
            "condition_field": self.condition_field,
            "condition_value": self.condition_value,
            "not_required_fields": self.not_required_fields,
            "if": {
                "properties": {
                    self.condition_field: {"not": {"const": self.condition_value}}
                }
            },
            "then": {"required": self.not_required_fields},
        }


class AtLeastOneOfValidator(BaseConstraintValidator):
    """Validates that at least one of multiple fields is present."""

    def __init__(self, *field_names: str):
        super().__init__()
        self.field_names = field_names

    def validate(self, model_instance: BaseModel) -> None:
        target = model_instance
        if hasattr(model_instance, "properties"):
            target = model_instance.properties

        present_fields = []
        for field_name in self.field_names:
            if hasattr(target, field_name) and getattr(target, field_name) is not None:
                present_fields.append(field_name)

        if not present_fields:
            raise ValueError(
                f"At least one of {', '.join(self.field_names)} must be present"
            )

    def get_json_schema_metadata(self) -> dict[str, Any]:
        return {
            "type": "at_least_one_of",
            "fields": list(self.field_names),
            "anyOf": [{"required": [field]} for field in self.field_names],
        }


class ConditionalEnumValidator(BaseConstraintValidator):
    """Validates enum field values based on another field's value."""

    def __init__(
        self,
        enum_field: str,
        condition_field: str,
        enum_mapping: dict[str, list[str]],
    ):
        super().__init__()
        self.enum_field = enum_field
        self.condition_field = condition_field
        self.enum_mapping = enum_mapping

    def validate(self, model_instance: BaseModel) -> None:
        target = model_instance
        if hasattr(model_instance, "properties"):
            target = model_instance.properties

        # Get values of both fields
        if not (
            hasattr(target, self.enum_field) and hasattr(target, self.condition_field)
        ):
            return

        enum_value = getattr(target, self.enum_field)
        condition_value = getattr(target, self.condition_field)

        # Skip validation if enum field is None (optional field)
        if enum_value is None:
            return

        # Check if condition value has a mapping
        if condition_value not in self.enum_mapping:
            return

        allowed_values = self.enum_mapping[condition_value]
        if enum_value not in allowed_values:
            allowed_list = ", ".join(f"'{v}'" for v in allowed_values)
            raise ValueError(
                f"Invalid {self.enum_field} '{enum_value}' for {self.condition_field} '{condition_value}'. "
                f"Allowed values: {allowed_list}"
            )

    def get_json_schema_metadata(self) -> dict[str, Any]:
        # Generate conditional schema using if/then structure
        conditions = []
        for condition_value, allowed_values in self.enum_mapping.items():
            conditions.append(
                {
                    "if": {
                        "properties": {self.condition_field: {"const": condition_value}}
                    },
                    "then": {"properties": {self.enum_field: {"enum": allowed_values}}},
                }
            )

        return {
            "type": "conditional_enum",
            "enum_field": self.enum_field,
            "condition_field": self.condition_field,
            "enum_mapping": self.enum_mapping,
            "allOf": conditions,
        }


def register_constraint(
    model_class: type[BaseModel], constraint: BaseConstraintValidator
):
    """Register a constraint for a model class."""
    class_name = model_class.__name__
    if class_name not in _constraint_registry:
        _constraint_registry[class_name] = []
    _constraint_registry[class_name].append(constraint)


# Decorators
def mutually_exclusive(*field_names: str):
    """Decorator to add mutually exclusive field validation."""

    def decorator(cls: type[BaseModel]) -> type[BaseModel]:
        constraint = MutuallyExclusiveValidator(*field_names)
        register_constraint(cls, constraint)
        return cls

    return decorator


def required_if(condition_field: str, condition_value: Any, required_fields: list[str]):
    """Decorator to add conditional required field validation."""

    def decorator(cls: type[BaseModel]) -> type[BaseModel]:
        constraint = RequiredIfValidator(
            condition_field, condition_value, required_fields
        )
        register_constraint(cls, constraint)
        return cls

    return decorator


def at_least_one_of(*field_names: str):
    """Decorator to add at-least-one-of validation."""

    def decorator(cls: type[BaseModel]) -> type[BaseModel]:
        constraint = AtLeastOneOfValidator(*field_names)
        register_constraint(cls, constraint)
        return cls

    return decorator


def not_required_if(
    condition_field: str, condition_value: Any, not_required_fields: list[str]
):
    """Decorator to add conditional not-required field validation."""

    def decorator(cls: type[BaseModel]) -> type[BaseModel]:
        constraint = NotRequiredIfValidator(
            condition_field, condition_value, not_required_fields
        )
        register_constraint(cls, constraint)
        return cls

    return decorator


def conditional_enum(
    enum_field: str, condition_field: str, enum_mapping: dict[str, list[str]]
):
    """Decorator to add conditional enum validation."""

    def decorator(cls: type[BaseModel]) -> type[BaseModel]:
        constraint = ConditionalEnumValidator(enum_field, condition_field, enum_mapping)
        register_constraint(cls, constraint)
        return cls

    return decorator


# Mixin class with constraint validation
class ConstraintValidatedModel:
    """Mixin class that provides constraint validation capabilities.

    This is a true mixin - it doesn't inherit from BaseModel to avoid MRO issues.
    Use it like: class MyModel(BaseModel, ConstraintValidatedModel)
    """

    @model_validator(mode="after")
    def validate_constraints(self):
        """Run all registered constraints for this model and its parent classes."""
        all_constraints = []

        # Collect constraints from this class and all parent classes
        for cls in self.__class__.__mro__:
            class_constraints = _constraint_registry.get(cls.__name__, [])
            all_constraints.extend(class_constraints)

        # Run all constraints
        for constraint in all_constraints:
            constraint.validate(self)
        return self

    @classmethod
    def model_json_schema(
        cls, by_alias: bool = True, ref_template: str = "#/$defs/{model}"
    ) -> dict[str, Any]:
        """Override to add constraint metadata to JSON Schema."""
        # Get the base schema - handle MRO properly
        # Find BaseModel in MRO and call its model_json_schema method
        from pydantic import BaseModel

        for base_cls in cls.__mro__:
            if base_cls is BaseModel:
                schema = base_cls.model_json_schema.__func__(
                    cls, by_alias=by_alias, ref_template=ref_template
                )
                break
        else:
            # Fallback if BaseModel not found
            schema = {"type": "object", "properties": {}, "title": cls.__name__}

        # Add constraint metadata from this class and all parent classes
        all_constraints = []
        for parent_cls in cls.__mro__:
            class_constraints = _constraint_registry.get(parent_cls.__name__, [])
            all_constraints.extend(class_constraints)

        constraints = all_constraints
        if constraints:
            for constraint in constraints:
                constraint_metadata = constraint.get_json_schema_metadata()
                if constraint_metadata:
                    # Add conditional schema directly to JSON Schema
                    if constraint_metadata.get("if") and constraint_metadata.get(
                        "then"
                    ):
                        conditional_schema = {
                            "if": constraint_metadata["if"],
                            "then": constraint_metadata.get("then"),
                        }
                        if constraint_metadata.get("else"):
                            conditional_schema["else"] = constraint_metadata["else"]

                        schema.setdefault("allOf", []).append(conditional_schema)

                    if constraint_metadata.get("anyOf"):
                        schema.setdefault("anyOf", []).extend(
                            constraint_metadata["anyOf"]
                        )

                    if constraint_metadata.get("not"):
                        schema.setdefault("allOf", []).append(
                            {"not": constraint_metadata["not"]}
                        )

                    # Also add as custom extension for tooling
                    schema.setdefault("x-constraints", []).append(constraint_metadata)

        return schema
