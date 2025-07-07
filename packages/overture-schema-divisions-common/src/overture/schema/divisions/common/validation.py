"""Division-specific validation constraints."""

from typing import Any

from pydantic import BaseModel
from overture.schema.validation.mixin import (
    BaseConstraintValidator,
    register_constraint,
)


class ParentDivisionValidator(BaseConstraintValidator):
    """Validates parent division logic: parent_division_id is required unless field equals exempt value."""

    def __init__(self, field_name: str, exempt_value: Any):
        super().__init__()
        self.field_name = field_name
        self.exempt_value = exempt_value

    def validate(self, model_instance: BaseModel) -> None:
        # Handle nested properties if needed
        target = model_instance
        if hasattr(model_instance, "properties"):
            target = model_instance.properties

        if hasattr(target, self.field_name) and hasattr(target, "parent_division_id"):
            field_value = getattr(target, self.field_name)
            parent_division_id = target.parent_division_id

            if field_value == self.exempt_value and parent_division_id is not None:
                raise ValueError(
                    f"parent_division_id must not be present when {self.field_name} is {self.exempt_value}"
                )
            elif field_value != self.exempt_value and parent_division_id is None:
                raise ValueError(
                    f"parent_division_id is required when {self.field_name} is not {self.exempt_value} (current: {field_value})"
                )

    def get_json_schema_metadata(self) -> dict[str, Any]:
        return {
            "type": "parent_division_required_unless",
            "field_name": self.field_name,
            "exempt_value": self.exempt_value,
            "if": {"properties": {self.field_name: {"const": self.exempt_value}}},
            "then": {"not": {"required": ["parent_division_id"]}},
            "else": {"required": ["parent_division_id"]},
        }


def parent_division_required_unless(field_name: str, exempt_value: Any):
    """Decorator to add parent division validation: parent_division_id is required unless field equals exempt value."""

    def decorator(cls: type[BaseModel]) -> type[BaseModel]:
        constraint = ParentDivisionValidator(field_name, exempt_value)
        register_constraint(cls, constraint)
        return cls

    return decorator
