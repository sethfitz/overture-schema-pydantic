"""Tests for parent division constraint validation."""

from enum import Enum

import pytest
from pydantic import BaseModel, ValidationError

from overture.schema.divisions.common.validation import (
    ParentDivisionValidator,
    parent_division_required_unless,
)
from overture.schema.validation import ConstraintValidatedModel
from overture.schema.validation.mixin import _constraint_registry


class PlaceType(str, Enum):
    """Test enum for place types."""

    COUNTRY = "country"
    REGION = "region"
    LOCALITY = "locality"


@pytest.fixture(autouse=True)
def clear_constraint_registry():
    """Clear the constraint registry before each test to avoid interference."""
    _constraint_registry.clear()
    yield
    _constraint_registry.clear()


class TestParentDivisionValidator:
    """Test parent division constraint validation."""

    def test_parent_division_validator_direct(self):
        """Test ParentDivisionValidator directly."""

        class TestModel(BaseModel):
            subtype: PlaceType
            parent_division_id: str | None = None

        validator = ParentDivisionValidator("subtype", PlaceType.COUNTRY)

        # Valid: country without parent
        model = TestModel(subtype=PlaceType.COUNTRY, parent_division_id=None)
        validator.validate(model)  # Should not raise

        # Valid: region with parent
        model = TestModel(subtype=PlaceType.REGION, parent_division_id="parent_id")
        validator.validate(model)  # Should not raise

        # Invalid: country with parent
        model = TestModel(subtype=PlaceType.COUNTRY, parent_division_id="parent_id")
        with pytest.raises(
            ValueError,
            match="parent_division_id must not be present when subtype is country",
        ):
            validator.validate(model)

        # Invalid: region without parent
        model = TestModel(subtype=PlaceType.REGION, parent_division_id=None)
        with pytest.raises(
            ValueError,
            match="parent_division_id is required when subtype is not country",
        ):
            validator.validate(model)

    def test_parent_division_constraint_decorator(self):
        """Test parent division constraint using decorator."""

        @parent_division_required_unless("subtype", PlaceType.COUNTRY)
        class DivisionModel(ConstraintValidatedModel, BaseModel):
            subtype: PlaceType
            parent_division_id: str | None = None

        # Valid: country without parent
        model = DivisionModel(subtype=PlaceType.COUNTRY, parent_division_id=None)
        assert model.subtype == PlaceType.COUNTRY
        assert model.parent_division_id is None

        # Valid: region with parent
        model = DivisionModel(subtype=PlaceType.REGION, parent_division_id="parent_id")
        assert model.subtype == PlaceType.REGION
        assert model.parent_division_id == "parent_id"

        # Invalid: country with parent
        with pytest.raises(ValidationError) as exc_info:
            DivisionModel(subtype=PlaceType.COUNTRY, parent_division_id="parent_id")
        assert "parent_division_id must not be present when subtype is country" in str(
            exc_info.value
        )

        # Invalid: region without parent
        with pytest.raises(ValidationError) as exc_info:
            DivisionModel(subtype=PlaceType.REGION, parent_division_id=None)
        assert "parent_division_id is required when subtype is not country" in str(
            exc_info.value
        )

    def test_parent_division_nested_properties(self):
        """Test parent division constraint with nested properties."""

        class PropertiesModel(BaseModel):
            subtype: PlaceType
            parent_division_id: str | None = None

        @parent_division_required_unless("subtype", PlaceType.COUNTRY)
        class FeatureModel(ConstraintValidatedModel, BaseModel):
            properties: PropertiesModel

        # Valid: country without parent
        model = FeatureModel(
            properties=PropertiesModel(
                subtype=PlaceType.COUNTRY, parent_division_id=None
            )
        )
        assert model.properties.subtype == PlaceType.COUNTRY

        # Invalid: country with parent
        with pytest.raises(ValidationError) as exc_info:
            FeatureModel(
                properties=PropertiesModel(
                    subtype=PlaceType.COUNTRY, parent_division_id="parent"
                )
            )
        assert "parent_division_id must not be present when subtype is country" in str(
            exc_info.value
        )

    def test_parent_division_json_schema(self):
        """Test JSON schema generation for parent division constraint."""

        @parent_division_required_unless("subtype", PlaceType.COUNTRY)
        class DivisionModel(ConstraintValidatedModel, BaseModel):
            subtype: PlaceType
            parent_division_id: str | None = None

        schema = DivisionModel.model_json_schema()

        # Should have constraint metadata
        assert "x-constraints" in schema
        assert len(schema["x-constraints"]) == 1

        constraint = schema["x-constraints"][0]
        assert constraint["type"] == "parent_division_required_unless"
        assert constraint["field_name"] == "subtype"
        assert constraint["exempt_value"] == PlaceType.COUNTRY

        # Should have conditional schema
        assert "allOf" in schema
        assert len(schema["allOf"]) == 1

        condition = schema["allOf"][0]
        assert "if" in condition
        assert "then" in condition
        assert "else" in condition
