"""Comprehensive tests for mixin-based constraint validation."""

from typing import Optional, List
from enum import Enum
import pytest
from pydantic import BaseModel, Field, ValidationError

from overture.schema.validation import (
    # Mixin classes and decorators
    ConstraintValidatedModel,
    BaseConstraintValidator,
    MutuallyExclusiveValidator,
    RequiredIfValidator,
    NotRequiredIfValidator,
    AtLeastOneOfValidator,
    # Decorators
    mutually_exclusive,
    required_if,
    not_required_if,
    at_least_one_of,
)
from overture.schema.divisions.common.validation import (
    ParentDivisionValidator,
    parent_division_required_unless,
)
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


class TestBaseConstraintValidator:
    """Test the base constraint validator functionality."""

    def test_base_constraint_validator_abstract(self):
        """Test that BaseConstraintValidator is properly abstract."""
        with pytest.raises(TypeError):
            BaseConstraintValidator()

    def test_custom_constraint_validator(self):
        """Test creating a custom constraint validator."""

        class CustomValidator(BaseConstraintValidator):
            def __init__(self, required_value: str):
                super().__init__()
                self.required_value = required_value

            def validate(self, model_instance: BaseModel) -> None:
                if hasattr(model_instance, "custom_field"):
                    if model_instance.custom_field != self.required_value:
                        raise ValueError(f"custom_field must be {self.required_value}")

            def get_json_schema_metadata(self):
                return {
                    "type": "custom_constraint",
                    "required_value": self.required_value,
                }

        # Test the custom validator
        validator = CustomValidator("expected")

        class TestModel(BaseModel):
            custom_field: str

        # Valid case
        model = TestModel(custom_field="expected")
        validator.validate(model)  # Should not raise

        # Invalid case
        model = TestModel(custom_field="wrong")
        with pytest.raises(ValueError, match="custom_field must be expected"):
            validator.validate(model)

        # Test JSON schema metadata
        metadata = validator.get_json_schema_metadata()
        assert metadata["type"] == "custom_constraint"
        assert metadata["required_value"] == "expected"


class TestConstraintValidatedModel:
    """Test the ConstraintValidatedModel base class."""

    def test_constraint_validated_model_inheritance(self):
        """Test that ConstraintValidatedModel can be inherited."""

        class TestModel(ConstraintValidatedModel, BaseModel):
            name: str

        # Should create without issues
        model = TestModel(name="test")
        assert model.name == "test"

    def test_constraint_validated_model_with_no_constraints(self):
        """Test that models without constraints work normally."""

        class TestModel(ConstraintValidatedModel, BaseModel):
            name: str
            value: int = 42

        model = TestModel(name="test", value=100)
        assert model.name == "test"
        assert model.value == 100

    def test_json_schema_generation_no_constraints(self):
        """Test JSON schema generation for models without constraints."""

        class TestModel(ConstraintValidatedModel, BaseModel):
            name: str
            value: int = 42

        schema = TestModel.model_json_schema()

        # Should have standard properties
        assert "properties" in schema
        assert "name" in schema["properties"]
        assert "value" in schema["properties"]

        # Should not have constraint-specific fields
        assert "x-constraints" not in schema
        assert "allOf" not in schema


class TestParentDivisionValidator:
    """Test parent division constraint validation."""

    def test_parent_division_validator_direct(self):
        """Test ParentDivisionValidator directly."""

        class TestModel(BaseModel):
            subtype: PlaceType
            parent_division_id: Optional[str] = None

        validator = ParentDivisionValidator(PlaceType.COUNTRY)

        # Valid: country without parent
        model = TestModel(subtype=PlaceType.COUNTRY, parent_division_id=None)
        validator.validate(model)  # Should not raise

        # Valid: region with parent
        model = TestModel(subtype=PlaceType.REGION, parent_division_id="parent_id")
        validator.validate(model)  # Should not raise

        # Invalid: country with parent
        model = TestModel(subtype=PlaceType.COUNTRY, parent_division_id="parent_id")
        with pytest.raises(
            ValueError, match="Countries must not have parent_division_id"
        ):
            validator.validate(model)

        # Invalid: region without parent
        model = TestModel(subtype=PlaceType.REGION, parent_division_id=None)
        with pytest.raises(
            ValueError, match="parent_division_id is required for sub-country divisions"
        ):
            validator.validate(model)

    def test_parent_division_constraint_decorator(self):
        """Test parent division constraint using decorator."""

        @parent_division_required_unless("subtype", PlaceType.COUNTRY)
        class DivisionModel(ConstraintValidatedModel, BaseModel):
            subtype: PlaceType
            parent_division_id: Optional[str] = None

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
        assert "Countries must not have parent_division_id" in str(exc_info.value)

        # Invalid: region without parent
        with pytest.raises(ValidationError) as exc_info:
            DivisionModel(subtype=PlaceType.REGION, parent_division_id=None)
        assert "parent_division_id is required for sub-country divisions" in str(
            exc_info.value
        )

    def test_parent_division_nested_properties(self):
        """Test parent division constraint with nested properties."""

        class PropertiesModel(BaseModel):
            subtype: PlaceType
            parent_division_id: Optional[str] = None

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
        assert "Countries must not have parent_division_id" in str(exc_info.value)

    def test_parent_division_json_schema(self):
        """Test JSON schema generation for parent division constraint."""

        @parent_division_required_unless("subtype", PlaceType.COUNTRY)
        class DivisionModel(ConstraintValidatedModel, BaseModel):
            subtype: PlaceType
            parent_division_id: Optional[str] = None

        schema = DivisionModel.model_json_schema()

        # Should have constraint metadata
        assert "x-constraints" in schema
        assert len(schema["x-constraints"]) == 1

        constraint = schema["x-constraints"][0]
        assert constraint["type"] == "parent_division_constraint"
        assert constraint["country_subtype"] == PlaceType.COUNTRY

        # Should have conditional schema
        assert "allOf" in schema
        assert len(schema["allOf"]) == 1

        condition = schema["allOf"][0]
        assert "if" in condition
        assert "then" in condition
        assert "else" in condition


class TestMutuallyExclusiveValidator:
    """Test mutually exclusive constraint validation."""

    def test_mutually_exclusive_validator_direct(self):
        """Test MutuallyExclusiveValidator directly."""

        class TestModel(BaseModel):
            field_a: Optional[bool] = None
            field_b: Optional[bool] = None

        validator = MutuallyExclusiveValidator("field_a", "field_b")

        # Valid: neither field is True
        model = TestModel(field_a=False, field_b=False)
        validator.validate(model)  # Should not raise

        # Valid: only one field is True
        model = TestModel(field_a=True, field_b=False)
        validator.validate(model)  # Should not raise

        model = TestModel(field_a=False, field_b=True)
        validator.validate(model)  # Should not raise

        # Valid: fields are None
        model = TestModel(field_a=None, field_b=None)
        validator.validate(model)  # Should not raise

        # Invalid: both fields are True
        model = TestModel(field_a=True, field_b=True)
        with pytest.raises(
            ValueError, match="are mutually exclusive and cannot all be true"
        ):
            validator.validate(model)

    def test_mutually_exclusive_constraint_decorator(self):
        """Test mutually exclusive constraint using decorator."""

        @mutually_exclusive("is_land", "is_territorial")
        class BoundaryModel(ConstraintValidatedModel, BaseModel):
            is_land: Optional[bool] = None
            is_territorial: Optional[bool] = None

        # Valid cases
        model = BoundaryModel(is_land=True, is_territorial=False)
        assert model.is_land is True
        assert model.is_territorial is False

        model = BoundaryModel(is_land=False, is_territorial=True)
        assert model.is_land is False
        assert model.is_territorial is True

        model = BoundaryModel(is_land=None, is_territorial=None)
        assert model.is_land is None
        assert model.is_territorial is None

        # Invalid case: both True
        with pytest.raises(ValidationError) as exc_info:
            BoundaryModel(is_land=True, is_territorial=True)
        assert "are mutually exclusive and cannot all be true" in str(exc_info.value)

    def test_mutually_exclusive_multiple_fields(self):
        """Test mutually exclusive constraint with more than 2 fields."""

        @mutually_exclusive("option_a", "option_b", "option_c")
        class OptionsModel(ConstraintValidatedModel, BaseModel):
            option_a: Optional[bool] = None
            option_b: Optional[bool] = None
            option_c: Optional[bool] = None

        # Valid: only one option True
        model = OptionsModel(option_a=True, option_b=False, option_c=False)
        assert model.option_a is True

        # Invalid: multiple options True
        with pytest.raises(ValidationError) as exc_info:
            OptionsModel(option_a=True, option_b=True, option_c=False)
        assert "are mutually exclusive and cannot all be true" in str(exc_info.value)

    def test_mutually_exclusive_json_schema(self):
        """Test JSON schema generation for mutually exclusive constraint."""

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


class TestConditionalRequiredValidator:
    """Test conditional required constraint validation."""

    def test_conditional_required_validator_direct(self):
        """Test RequiredIfValidator directly."""

        class TestModel(BaseModel):
            type_field: str
            required_field: Optional[str] = None

        validator = RequiredIfValidator("type_field", "special", ["required_field"])

        # Valid: condition not met, field can be None
        model = TestModel(type_field="normal", required_field=None)
        validator.validate(model)  # Should not raise

        # Valid: condition met, field provided
        model = TestModel(type_field="special", required_field="value")
        validator.validate(model)  # Should not raise

        # Invalid: condition met, field missing
        model = TestModel(type_field="special", required_field=None)
        with pytest.raises(
            ValueError,
            match="Field 'required_field' is required when type_field = special",
        ):
            validator.validate(model)

    def test_conditional_required_constraint_decorator(self):
        """Test conditional required constraint using decorator."""

        @required_if("subtype", "road", ["class_"])
        @required_if("subtype", "rail", ["class_"])
        class SegmentModel(ConstraintValidatedModel, BaseModel):
            subtype: str
            class_: Optional[str] = None

        # Valid: subtype doesn't require class_
        model = SegmentModel(subtype="water", class_=None)
        assert model.subtype == "water"
        assert model.class_ is None

        # Valid: road subtype with class_
        model = SegmentModel(subtype="road", class_="primary")
        assert model.subtype == "road"
        assert model.class_ == "primary"

        # Valid: rail subtype with class_
        model = SegmentModel(subtype="rail", class_="passenger")
        assert model.subtype == "rail"
        assert model.class_ == "passenger"

        # Invalid: road subtype without class_
        with pytest.raises(ValidationError) as exc_info:
            SegmentModel(subtype="road", class_=None)
        assert "Field 'class_' is required when subtype = road" in str(exc_info.value)

        # Invalid: rail subtype without class_
        with pytest.raises(ValidationError) as exc_info:
            SegmentModel(subtype="rail", class_=None)
        assert "Field 'class_' is required when subtype = rail" in str(exc_info.value)

    def test_conditional_required_multiple_fields(self):
        """Test conditional required constraint with multiple required fields."""

        @required_if("type", "complex", ["field_a", "field_b"])
        class TestModel(ConstraintValidatedModel, BaseModel):
            type: str
            field_a: Optional[str] = None
            field_b: Optional[str] = None

        # Valid: condition not met
        model = TestModel(type="simple", field_a=None, field_b=None)
        assert model.type == "simple"

        # Valid: condition met, all fields provided
        model = TestModel(type="complex", field_a="value_a", field_b="value_b")
        assert model.type == "complex"
        assert model.field_a == "value_a"
        assert model.field_b == "value_b"

        # Invalid: condition met, field_a missing
        with pytest.raises(ValidationError) as exc_info:
            TestModel(type="complex", field_a=None, field_b="value_b")
        assert "Field 'field_a' is required when type = complex" in str(exc_info.value)


class TestConditionalNotRequiredValidator:
    """Test conditional not required constraint validation."""

    def test_conditional_not_required_validator_direct(self):
        """Test NotRequiredIfValidator directly."""

        class TestModel(BaseModel):
            subtype: PlaceType
            country: Optional[str] = None

        validator = NotRequiredIfValidator("subtype", PlaceType.COUNTRY, ["country"])

        # Valid: country subtype, country can be None
        model = TestModel(subtype=PlaceType.COUNTRY, country=None)
        validator.validate(model)  # Should not raise

        # Valid: non-country subtype, country provided
        model = TestModel(subtype=PlaceType.REGION, country="US")
        validator.validate(model)  # Should not raise

        # Invalid: non-country subtype, country missing
        model = TestModel(subtype=PlaceType.REGION, country=None)
        with pytest.raises(
            ValueError, match="Field 'country' is required when subtype != country"
        ):
            validator.validate(model)

    def test_conditional_not_required_constraint_decorator(self):
        """Test conditional not required constraint using decorator."""

        @not_required_if("subtype", PlaceType.COUNTRY, ["country"])
        class BoundaryModel(ConstraintValidatedModel, BaseModel):
            subtype: PlaceType
            country: Optional[str] = None

        # Valid: country subtype, no country field needed
        model = BoundaryModel(subtype=PlaceType.COUNTRY, country=None)
        assert model.subtype == PlaceType.COUNTRY
        assert model.country is None

        # Valid: region subtype, country provided
        model = BoundaryModel(subtype=PlaceType.REGION, country="US")
        assert model.subtype == PlaceType.REGION
        assert model.country == "US"

        # Invalid: region subtype, country missing
        with pytest.raises(ValidationError) as exc_info:
            BoundaryModel(subtype=PlaceType.REGION, country=None)
        assert "Field 'country' is required when subtype != country" in str(
            exc_info.value
        )


class TestAtLeastOneOfValidator:
    """Test at-least-one-of constraint validation."""

    def test_at_least_one_of_validator_direct(self):
        """Test AtLeastOneOfValidator directly."""

        class TestModel(BaseModel):
            max_speed: Optional[str] = None
            min_speed: Optional[str] = None

        validator = AtLeastOneOfValidator("max_speed", "min_speed")

        # Valid: max_speed provided
        model = TestModel(max_speed="50", min_speed=None)
        validator.validate(model)  # Should not raise

        # Valid: min_speed provided
        model = TestModel(max_speed=None, min_speed="30")
        validator.validate(model)  # Should not raise

        # Valid: both provided
        model = TestModel(max_speed="50", min_speed="30")
        validator.validate(model)  # Should not raise

        # Invalid: neither provided
        model = TestModel(max_speed=None, min_speed=None)
        with pytest.raises(
            ValueError, match="At least one of max_speed, min_speed must be present"
        ):
            validator.validate(model)

    def test_at_least_one_of_constraint_decorator(self):
        """Test at-least-one-of constraint using decorator."""

        @at_least_one_of("max_speed", "min_speed")
        class SpeedRuleModel(ConstraintValidatedModel, BaseModel):
            max_speed: Optional[str] = None
            min_speed: Optional[str] = None

        # Valid cases
        model = SpeedRuleModel(max_speed="50", min_speed=None)
        assert model.max_speed == "50"
        assert model.min_speed is None

        model = SpeedRuleModel(max_speed=None, min_speed="30")
        assert model.max_speed is None
        assert model.min_speed == "30"

        model = SpeedRuleModel(max_speed="50", min_speed="30")
        assert model.max_speed == "50"
        assert model.min_speed == "30"

        # Invalid case: neither provided
        with pytest.raises(ValidationError) as exc_info:
            SpeedRuleModel(max_speed=None, min_speed=None)
        assert "At least one of max_speed, min_speed must be present" in str(
            exc_info.value
        )

    def test_at_least_one_of_multiple_fields(self):
        """Test at-least-one-of constraint with multiple fields."""

        @at_least_one_of("field_a", "field_b", "field_c")
        class TestModel(ConstraintValidatedModel, BaseModel):
            field_a: Optional[str] = None
            field_b: Optional[str] = None
            field_c: Optional[str] = None

        # Valid: one field provided
        model = TestModel(field_a="value", field_b=None, field_c=None)
        assert model.field_a == "value"

        # Valid: multiple fields provided
        model = TestModel(field_a="value_a", field_b="value_b", field_c=None)
        assert model.field_a == "value_a"
        assert model.field_b == "value_b"

        # Invalid: no fields provided
        with pytest.raises(ValidationError) as exc_info:
            TestModel(field_a=None, field_b=None, field_c=None)
        assert "At least one of field_a, field_b, field_c must be present" in str(
            exc_info.value
        )


class TestMultipleConstraints:
    """Test models with multiple constraints applied."""

    def test_multiple_constraint_decorators(self):
        """Test applying multiple constraint decorators to one model."""

        @parent_division_required_unless("subtype", PlaceType.COUNTRY)
        @mutually_exclusive("is_land", "is_territorial")
        @required_if("subtype", PlaceType.REGION, ["region_code"])
        class ComplexModel(ConstraintValidatedModel, BaseModel):
            subtype: PlaceType
            parent_division_id: Optional[str] = None
            is_land: Optional[bool] = None
            is_territorial: Optional[bool] = None
            region_code: Optional[str] = None

        # Valid: country with no parent, land boundary, no region code needed
        model = ComplexModel(
            subtype=PlaceType.COUNTRY,
            parent_division_id=None,
            is_land=True,
            is_territorial=False,
            region_code=None,
        )
        assert model.subtype == PlaceType.COUNTRY
        assert model.is_land is True

        # Valid: region with parent, territorial boundary, region code provided
        model = ComplexModel(
            subtype=PlaceType.REGION,
            parent_division_id="parent",
            is_land=False,
            is_territorial=True,
            region_code="US-CA",
        )
        assert model.subtype == PlaceType.REGION
        assert model.region_code == "US-CA"

        # Invalid: violates parent division constraint
        with pytest.raises(ValidationError) as exc_info:
            ComplexModel(
                subtype=PlaceType.COUNTRY,
                parent_division_id="should_not_have_parent",
                is_land=True,
                is_territorial=False,
                region_code=None,
            )
        assert "Countries must not have parent_division_id" in str(exc_info.value)

        # Invalid: violates mutually exclusive constraint
        with pytest.raises(ValidationError) as exc_info:
            ComplexModel(
                subtype=PlaceType.REGION,
                parent_division_id="parent",
                is_land=True,
                is_territorial=True,  # Both True - invalid
                region_code="US-CA",
            )
        assert "are mutually exclusive and cannot all be true" in str(exc_info.value)

        # Invalid: violates conditional required constraint
        with pytest.raises(ValidationError) as exc_info:
            ComplexModel(
                subtype=PlaceType.REGION,
                parent_division_id="parent",
                is_land=True,
                is_territorial=False,
                region_code=None,  # Required when subtype is REGION
            )
        assert "Field 'region_code' is required when subtype = region" in str(
            exc_info.value
        )

    def test_multiple_constraints_json_schema(self):
        """Test JSON schema generation with multiple constraints."""

        @parent_division_required_unless("subtype", PlaceType.COUNTRY)
        @mutually_exclusive("field_a", "field_b")
        @at_least_one_of("required_a", "required_b")
        class MultiConstraintModel(ConstraintValidatedModel, BaseModel):
            subtype: PlaceType
            parent_division_id: Optional[str] = None
            field_a: Optional[bool] = None
            field_b: Optional[bool] = None
            required_a: Optional[str] = None
            required_b: Optional[str] = None

        schema = MultiConstraintModel.model_json_schema()

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


class TestConstraintInheritance:
    """Test constraint inheritance and complex model hierarchies."""

    def test_constraint_inheritance(self):
        """Test that constraints work with model inheritance."""

        @mutually_exclusive("field_a", "field_b")
        class TestBaseModel(ConstraintValidatedModel, BaseModel):
            field_a: Optional[bool] = None
            field_b: Optional[bool] = None

        @at_least_one_of("required_c", "required_d")
        class DerivedModel(TestBaseModel):
            required_c: Optional[str] = None
            required_d: Optional[str] = None

        # Valid: satisfies both constraints
        model = DerivedModel(
            field_a=True, field_b=False, required_c="value", required_d=None
        )
        assert model.field_a is True
        assert model.required_c == "value"

        # Invalid: violates base class constraint
        with pytest.raises(ValidationError) as exc_info:
            DerivedModel(
                field_a=True,
                field_b=True,  # Violates mutually exclusive
                required_c="value",
                required_d=None,
            )
        assert "are mutually exclusive" in str(exc_info.value)

        # Invalid: violates derived class constraint
        with pytest.raises(ValidationError) as exc_info:
            DerivedModel(
                field_a=True,
                field_b=False,
                required_c=None,
                required_d=None,  # Violates at_least_one_of
            )
        assert "At least one of required_c, required_d must be present" in str(
            exc_info.value
        )


class TestConstraintErrorHandling:
    """Test error handling and edge cases."""

    def test_constraint_with_missing_fields(self):
        """Test constraints when referenced fields don't exist."""

        @parent_division_required_unless("subtype", PlaceType.COUNTRY)
        class IncompleteModel(ConstraintValidatedModel, BaseModel):
            # Missing subtype and parent_division_id fields
            name: str

        # Should not raise validation errors for missing fields
        # (constraint should handle missing fields gracefully)
        model = IncompleteModel(name="test")
        assert model.name == "test"

    def test_constraint_validator_without_mixin(self):
        """Test that decorators work but validation won't be applied without the mixin."""

        # This should not raise - decorators can be applied to any class
        # but validation won't happen without ConstraintValidatedModel
        @parent_division_required_unless("subtype", PlaceType.COUNTRY)
        class InvalidModel(BaseModel):  # Missing ConstraintValidatedModel
            subtype: PlaceType
            parent_division_id: Optional[str] = None

        # This should NOT fail validation since ConstraintValidatedModel isn't mixed in
        model = InvalidModel(
            subtype=PlaceType.COUNTRY, parent_division_id="should_fail_but_wont"
        )
        assert model.subtype == PlaceType.COUNTRY

    def test_constraint_validation_order(self):
        """Test that constraints are validated in the correct order."""

        # This test ensures that field validation happens before constraint validation
        @required_if("type_field", "special", ["required_field"])
        class OrderTestModel(ConstraintValidatedModel, BaseModel):
            type_field: str
            required_field: Optional[str] = None

        # Field validation should catch invalid type_field before constraint validation
        with pytest.raises(ValidationError) as exc_info:
            # This should fail due to validation of enum field, not constraint
            OrderTestModel(type_field=123, required_field=None)  # Invalid type

        # Constraint validation should catch missing required field
        with pytest.raises(ValidationError) as exc_info:
            OrderTestModel(type_field="special", required_field=None)
        assert "Field 'required_field' is required" in str(exc_info.value)

    def test_json_schema_with_no_constraints(self):
        """Test JSON schema generation when no constraints are registered."""

        class PlainModel(ConstraintValidatedModel, BaseModel):
            name: str
            value: int

        schema = PlainModel.model_json_schema()

        # Should generate normal schema without constraint extensions
        assert "properties" in schema
        assert "x-constraints" not in schema
        assert "allOf" not in schema


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    def test_geojson_feature_model(self):
        """Test constraint validation on a GeoJSON-like feature model."""

        class PropertiesModel(BaseModel):
            subtype: PlaceType
            parent_division_id: Optional[str] = None
            is_land: Optional[bool] = None
            is_territorial: Optional[bool] = None

        @parent_division_required_unless("subtype", PlaceType.COUNTRY)
        @mutually_exclusive("is_land", "is_territorial")
        class FeatureModel(ConstraintValidatedModel, BaseModel):
            id: str
            type: str = "Feature"
            properties: PropertiesModel
            geometry: dict

        # Valid feature
        feature_data = {
            "id": "test-feature",
            "properties": {
                "subtype": PlaceType.REGION,
                "parent_division_id": "US",
                "is_land": True,
                "is_territorial": False,
            },
            "geometry": {"type": "Point", "coordinates": [0, 0]},
        }

        model = FeatureModel(**feature_data)
        assert model.id == "test-feature"
        assert model.properties.subtype == PlaceType.REGION

        # Invalid feature - violates parent division constraint
        invalid_feature_data = {
            "id": "invalid-feature",
            "properties": {
                "subtype": PlaceType.COUNTRY,
                "parent_division_id": "should_not_have_parent",  # Invalid for country
                "is_land": True,
                "is_territorial": False,
            },
            "geometry": {"type": "Point", "coordinates": [0, 0]},
        }

        with pytest.raises(ValidationError) as exc_info:
            FeatureModel(**invalid_feature_data)
        assert "Countries must not have parent_division_id" in str(exc_info.value)

    def test_transportation_rule_model(self):
        """Test constraint validation on transportation rule models."""

        @at_least_one_of("max_speed", "min_speed")
        @required_if("is_variable", True, ["conditions"])
        class SpeedLimitRule(ConstraintValidatedModel, BaseModel):
            max_speed: Optional[dict] = None
            min_speed: Optional[dict] = None
            is_variable: bool = False
            conditions: Optional[List[str]] = None

        # Valid: has max_speed, not variable
        rule = SpeedLimitRule(
            max_speed={"value": 50, "unit": "km/h"},
            min_speed=None,
            is_variable=False,
            conditions=None,
        )
        assert rule.max_speed["value"] == 50

        # Valid: variable speed with conditions
        rule = SpeedLimitRule(
            max_speed={"value": 50, "unit": "km/h"},
            min_speed=None,
            is_variable=True,
            conditions=["weather_dependent"],
        )
        assert rule.is_variable is True
        assert rule.conditions == ["weather_dependent"]

        # Invalid: no speeds provided
        with pytest.raises(ValidationError) as exc_info:
            SpeedLimitRule(
                max_speed=None, min_speed=None, is_variable=False, conditions=None
            )
        assert "At least one of max_speed, min_speed must be present" in str(
            exc_info.value
        )

        # Invalid: variable but no conditions
        with pytest.raises(ValidationError) as exc_info:
            SpeedLimitRule(
                max_speed={"value": 50, "unit": "km/h"},
                min_speed=None,
                is_variable=True,
                conditions=None,
            )
        assert "Field 'conditions' is required when is_variable = True" in str(
            exc_info.value
        )


if __name__ == "__main__":
    pytest.main([__file__])
