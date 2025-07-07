"""Test JSON Schema generation for mixin-based constraint validation."""

from typing import Optional
from enum import Enum
import pytest
from pydantic import BaseModel, Field

from overture.schema.validation.mixin import (
    ConstraintValidatedModel,
    mutually_exclusive,
    required_if,
    not_required_if,
    at_least_one_of,
    _constraint_registry,
)
from overture.schema.divisions.common.validation import (
    parent_division_required_unless,
)


class TestSubtype(str, Enum):
    """Test enum for subtypes."""

    COUNTRY = "country"
    REGION = "region"
    LOCALITY = "locality"


@pytest.fixture(autouse=True)
def clear_constraint_registry():
    """Clear the constraint registry before each test to avoid interference."""
    _constraint_registry.clear()
    yield
    _constraint_registry.clear()


class TestJSONSchemaGeneration:
    """Test JSON Schema generation for constraint-validated models."""

    def test_parent_division_constraint_json_schema(self):
        """Test JSON Schema generation for parent division constraint."""

        @parent_division_required_unless("subtype", TestSubtype.COUNTRY)
        class TestModel(ConstraintValidatedModel, BaseModel):
            subtype: TestSubtype
            parent_division_id: Optional[str] = None

        schema = TestModel.model_json_schema()

        # Should have constraint metadata
        assert "x-constraints" in schema
        assert len(schema["x-constraints"]) == 1

        constraint = schema["x-constraints"][0]
        assert constraint["type"] == "parent_division_constraint"
        assert constraint["country_subtype"] == TestSubtype.COUNTRY

        # Should have conditional schema in allOf
        assert "allOf" in schema
        assert len(schema["allOf"]) == 1

        condition = schema["allOf"][0]
        assert "if" in condition
        assert "then" in condition
        assert "else" in condition

        # Check if condition structure
        if_condition = condition["if"]
        assert "properties" in if_condition
        assert "subtype" in if_condition["properties"]
        assert if_condition["properties"]["subtype"]["const"] == TestSubtype.COUNTRY

        # Check then condition (country should NOT have parent_division_id required)
        then_condition = condition["then"]
        assert "not" in then_condition
        assert "required" in then_condition["not"]
        assert "parent_division_id" in then_condition["not"]["required"]

        # Check else condition (non-country should have parent_division_id required)
        else_condition = condition["else"]
        assert "required" in else_condition
        assert "parent_division_id" in else_condition["required"]

    def test_mutually_exclusive_constraint_json_schema(self):
        """Test JSON Schema generation for mutually exclusive constraint."""

        @mutually_exclusive("field_a", "field_b")
        class TestModel(ConstraintValidatedModel, BaseModel):
            field_a: Optional[bool] = None
            field_b: Optional[bool] = None

        schema = TestModel.model_json_schema()

        # Should have constraint metadata
        assert "x-constraints" in schema
        assert len(schema["x-constraints"]) == 1

        constraint = schema["x-constraints"][0]
        assert constraint["type"] == "mutually_exclusive"
        assert set(constraint["fields"]) == {"field_a", "field_b"}

        # Should have negative constraint in allOf
        assert "allOf" in schema
        assert len(schema["allOf"]) == 1

        condition = schema["allOf"][0]
        assert "not" in condition

    def test_conditional_required_constraint_json_schema(self):
        """Test JSON Schema generation for conditional required constraint."""

        @required_if("type_field", "special", ["required_field"])
        class TestModel(ConstraintValidatedModel, BaseModel):
            type_field: str
            required_field: Optional[str] = None

        schema = TestModel.model_json_schema()

        # Should have constraint metadata
        assert "x-constraints" in schema
        assert len(schema["x-constraints"]) == 1

        constraint = schema["x-constraints"][0]
        assert constraint["type"] == "required_if"
        assert constraint["condition_field"] == "type_field"
        assert constraint["condition_value"] == "special"
        assert constraint["required_fields"] == ["required_field"]

        # Should have conditional in allOf
        assert "allOf" in schema
        assert len(schema["allOf"]) == 1

        condition = schema["allOf"][0]
        assert "if" in condition
        assert "then" in condition

    def test_at_least_one_of_constraint_json_schema(self):
        """Test JSON Schema generation for at-least-one-of constraint."""

        @at_least_one_of("field_a", "field_b")
        class TestModel(ConstraintValidatedModel, BaseModel):
            field_a: Optional[str] = None
            field_b: Optional[str] = None

        schema = TestModel.model_json_schema()

        # Should have constraint metadata
        assert "x-constraints" in schema
        assert len(schema["x-constraints"]) == 1

        constraint = schema["x-constraints"][0]
        assert constraint["type"] == "at_least_one_of"
        assert set(constraint["fields"]) == {"field_a", "field_b"}

        # Should have anyOf constraint
        assert "anyOf" in schema
        assert len(schema["anyOf"]) == 2

        # Check anyOf structure
        any_of = schema["anyOf"]
        required_fields = []
        for condition in any_of:
            assert "required" in condition
            required_fields.extend(condition["required"])

        assert set(required_fields) == {"field_a", "field_b"}

    def test_multiple_constraints_json_schema(self):
        """Test JSON Schema generation with multiple constraints."""

        @parent_division_required_unless("subtype", TestSubtype.COUNTRY)
        @mutually_exclusive("flag_a", "flag_b")
        @at_least_one_of("required_a", "required_b")
        class TestModel(ConstraintValidatedModel, BaseModel):
            subtype: TestSubtype
            parent_division_id: Optional[str] = None
            flag_a: Optional[bool] = None
            flag_b: Optional[bool] = None
            required_a: Optional[str] = None
            required_b: Optional[str] = None

        schema = TestModel.model_json_schema()

        # Should have all constraint metadata
        assert "x-constraints" in schema
        assert len(schema["x-constraints"]) == 3

        constraint_types = {c["type"] for c in schema["x-constraints"]}
        expected_types = {
            "parent_division_constraint",
            "mutually_exclusive",
            "at_least_one_of",
        }
        assert constraint_types == expected_types

        # Should have multiple conditions in allOf
        assert "allOf" in schema
        assert (
            len(schema["allOf"]) >= 2
        )  # At least parent division and mutually exclusive

        # Should have anyOf for at_least_one_of constraint
        assert "anyOf" in schema
        assert len(schema["anyOf"]) >= 2  # For required_a and required_b

    def test_no_constraints_json_schema(self):
        """Test JSON Schema generation for models without constraints."""

        class TestModel(ConstraintValidatedModel, BaseModel):
            name: str
            value: int = 42

        schema = TestModel.model_json_schema()

        # Should have standard properties but no constraint extensions
        assert "properties" in schema
        assert "name" in schema["properties"]
        assert "value" in schema["properties"]

        # Should not have constraint-specific fields
        assert "x-constraints" not in schema
        assert "allOf" not in schema or len(schema.get("allOf", [])) == 0
        assert "anyOf" not in schema or len(schema.get("anyOf", [])) == 0

    def test_nested_constraint_json_schema(self):
        """Test JSON Schema generation for models with nested properties."""

        class NestedProperties(BaseModel):
            subtype: TestSubtype
            parent_division_id: Optional[str] = None

        @parent_division_required_unless("subtype", TestSubtype.COUNTRY)
        class TestModel(ConstraintValidatedModel, BaseModel):
            id: str
            properties: NestedProperties

        schema = TestModel.model_json_schema()

        # Should have constraint metadata even with nested structure
        assert "x-constraints" in schema
        assert len(schema["x-constraints"]) == 1

        constraint = schema["x-constraints"][0]
        assert constraint["type"] == "parent_division_constraint"

        # Should have conditional constraints
        assert "allOf" in schema
        assert len(schema["allOf"]) == 1

    def test_json_schema_structure_validity(self):
        """Test that generated JSON Schema has valid structure."""

        @parent_division_required_unless("subtype", TestSubtype.COUNTRY)
        @mutually_exclusive("is_active", "is_inactive")
        class TestModel(ConstraintValidatedModel, BaseModel):
            subtype: TestSubtype
            parent_division_id: Optional[str] = None
            is_active: Optional[bool] = None
            is_inactive: Optional[bool] = None
            name: str = Field(..., description="Model name")

        schema = TestModel.model_json_schema()

        # Should have standard JSON Schema structure
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "title" in schema

        # Should have required fields
        assert "required" in schema
        assert "subtype" in schema["required"]
        assert "name" in schema["required"]

        # Property definitions should be valid
        properties = schema["properties"]
        assert "subtype" in properties
        assert "name" in properties
        assert "parent_division_id" in properties

        # Enum should be properly defined
        if "$defs" in schema:
            assert "TestSubtype" in schema["$defs"]
            enum_def = schema["$defs"]["TestSubtype"]
            assert enum_def["type"] == "string"
            assert "enum" in enum_def

        # Extension fields should be properly structured
        assert "x-constraints" in schema
        for constraint in schema["x-constraints"]:
            assert "type" in constraint
            assert isinstance(constraint["type"], str)

        # Conditional fields should be properly structured
        if "allOf" in schema:
            for condition in schema["allOf"]:
                # Each condition should have proper JSON Schema structure
                assert isinstance(condition, dict)

    def test_constraint_metadata_completeness(self):
        """Test that constraint metadata includes all necessary information."""

        @parent_division_required_unless("subtype", TestSubtype.COUNTRY)
        class TestModel(ConstraintValidatedModel, BaseModel):
            subtype: TestSubtype
            parent_division_id: Optional[str] = None

        schema = TestModel.model_json_schema()

        assert "x-constraints" in schema
        constraint = schema["x-constraints"][0]

        # Should have all required metadata fields
        required_fields = ["type", "country_subtype", "if", "then", "else"]
        for field in required_fields:
            assert field in constraint, f"Missing required field: {field}"

        # Metadata should be serializable (no Python objects)
        import json

        try:
            json.dumps(constraint)
        except (TypeError, ValueError) as e:
            pytest.fail(f"Constraint metadata is not JSON serializable: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
