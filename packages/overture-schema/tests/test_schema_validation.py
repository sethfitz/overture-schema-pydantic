"""
Pytest-based test harness for validating Pydantic schemas against examples and counterexamples.
Similar to the TypeScript version but using pytest, with support for .disabled extensions.
"""

from pathlib import Path
from typing import Any, Dict, Generator, List, Tuple

import overture.schema.addresses.address.models  # noqa: F401
import overture.schema.base.bathymetry.models  # noqa: F401
import overture.schema.base.infrastructure.models  # noqa: F401
import overture.schema.base.land.models  # noqa: F401
import overture.schema.base.land_cover.models  # noqa: F401
import overture.schema.base.land_use.models  # noqa: F401
import overture.schema.base.water.models  # noqa: F401
import overture.schema.buildings.building.models  # noqa: F401
import overture.schema.buildings.building_part.models  # noqa: F401
import overture.schema.divisions.division.models  # noqa: F401
import overture.schema.divisions.division_area.models  # noqa: F401
import overture.schema.divisions.division_boundary.models  # noqa: F401
import overture.schema.places.place.models  # noqa: F401
import overture.schema.transportation.connector.models  # noqa: F401
import overture.schema.transportation.segment.models  # noqa: F401
import pytest
import yaml
from deepdiff import DeepDiff
from overture.schema.core.base import (
    parse_feature,
)
from shapely.geometry import shape
from yamlcore import CoreLoader


def load_feature(file_path: str) -> Dict[str, Any]:
    """Load a feature from JSON or YAML file and return flattened/tabular format."""
    with open(file_path, encoding="utf-8") as f:
        # use a YAML-1.2-compliant (which dropped support for yes/no boolean values) Loader
        feature = yaml.load(f, Loader=CoreLoader)
        return create_flat_variant(feature)


def create_flat_variant(feature: Dict[str, Any]) -> Dict[str, Any]:
    """Create a variant of the feature with flat/Parquet-style structure."""
    flat_feature = feature.copy()

    # Check if this is GeoJSON format that needs flattening
    if "properties" in flat_feature and flat_feature.get("type") == "Feature":
        # Flatten GeoJSON feature to match GeoParquet structure
        flat_feature.update(flat_feature["properties"])
        del flat_feature["properties"]
        # Remove the GeoJSON "type": "Feature" field
        if flat_feature.get("type") == "Feature":
            del flat_feature["type"]

    return flat_feature


def create_shapely_variant(feature: Dict[str, Any]) -> Dict[str, Any]:
    """Create a variant of the feature with flat structure and Shapely geometry."""
    # Start with flattened feature (input should already be flat from load_feature)
    shapely_feature = feature.copy()
    if "geometry" in shapely_feature and shapely_feature["geometry"]:
        try:
            shapely_feature["geometry"] = shape(shapely_feature["geometry"])
        except Exception as e:
            # leave geometry as GeoJSON if conversion fails
            print(f"Error converting geometry to Shapely: {e}")
            pass
    return shapely_feature


def create_wkb_variant(feature: Dict[str, Any]) -> Dict[str, Any]:
    """Create a variant of the feature with flat structure and WKB geometry."""
    # Start with flattened feature (input should already be flat from load_feature)
    wkb_feature = feature.copy()
    if "geometry" in wkb_feature and wkb_feature["geometry"]:
        try:
            # Convert GeoJSON -> Shapely -> WKB bytes
            shapely_geom = shape(wkb_feature["geometry"])
            wkb_bytes = shapely_geom.wkb
            wkb_feature["geometry"] = wkb_bytes
        except Exception as e:
            # leave geometry as GeoJSON if conversion fails
            print(f"Error converting geometry to WKB: {e}")
            pass
    return wkb_feature


def create_wkt_variant(feature: Dict[str, Any]) -> Dict[str, Any]:
    """Create a variant of the feature with flat structure and WKT geometry."""
    # Start with flattened feature (input should already be flat from load_feature)
    wkt_feature = feature.copy()
    if "geometry" in wkt_feature and wkt_feature["geometry"]:
        try:
            # Convert GeoJSON -> Shapely -> WKT string
            shapely_geom = shape(wkt_feature["geometry"])
            wkt_string = shapely_geom.wkt
            wkt_feature["geometry"] = wkt_string
        except Exception as e:
            # leave geometry as GeoJSON if conversion fails
            print(f"Error converting geometry to WKT: {e}")
            pass
    return wkt_feature


def convert_to_geojson_format(flattened_feature: Dict[str, Any]) -> Dict[str, Any]:
    """Convert flattened feature to GeoJSON format for comparison."""
    return {
        "type": "Feature",
        "id": flattened_feature.get("id", None),
        "geometry": flattened_feature.get("geometry", None),
        "properties": {
            k: v for k, v in flattened_feature.items() if k not in ["id", "geometry"]
        },
    }


def deep_compare_dicts(
    original: Dict[str, Any], parsed: Dict[str, Any]
) -> Tuple[bool, str]:
    """
    Perform deep comparison between original and parsed dictionaries.
    Returns (is_equal, differences_report).
    """
    diff = DeepDiff(original, parsed, ignore_order=True, significant_digits=15)

    if not diff:
        return True, ""

    # Format differences for readable output
    differences = []

    if "values_changed" in diff:
        differences.append("Value changes:")
        for key, change in diff["values_changed"].items():
            differences.append(
                f"  {key}: {change['old_value']} -> {change['new_value']}"
            )

    if "dictionary_item_added" in diff:
        differences.append("Added items:")
        for item in diff["dictionary_item_added"]:
            differences.append(f"  {item}")

    if "dictionary_item_removed" in diff:
        differences.append("Removed items:")
        for item in diff["dictionary_item_removed"]:
            differences.append(f"  {item}")

    if "type_changes" in diff:
        differences.append("Type changes:")
        for key, change in diff["type_changes"].items():
            differences.append(f"  {key}: {change['old_type']} -> {change['new_type']}")

    return False, "\n".join(differences)


def walk_directory(directory: Path) -> Generator[Path, None, None]:
    """Walk directory and yield all relevant files."""
    for file_path in directory.rglob("*"):
        if file_path.is_file() and file_path.suffix in {
            ".json",
            ".geojson",
            ".yaml",
            ".yml",
            ".disabled",
        }:
            yield file_path


def group_files_by_directory(files: List[Path], base_dir: Path) -> Dict[str, Any]:
    """Group files by their directory structure."""
    groups = {}

    for file_path in files:
        relative_path = file_path.relative_to(base_dir)
        parts = relative_path.parts

        if len(parts) == 1:
            # File in root directory
            if "" not in groups:
                groups[""] = []
            groups[""].append(str(file_path))
            continue

        # Navigate through directory parts
        current = groups
        dir_parts = parts[:-1]

        for part in dir_parts:
            if part not in current:
                current[part] = {}
            current = current[part]

        # Add file to final directory
        last_dir = dir_parts[-1] if dir_parts else ""
        if not isinstance(current.get(last_dir), list):
            current[last_dir] = []
        current[last_dir].append(str(file_path))

    return groups


def create_test_cases(
    group: Dict[str, Any], base_dir: Path, is_counterexample: bool = False
) -> List[Tuple[str, str, bool]]:
    """Create test cases from grouped files."""
    test_cases = []

    def collect_files(g: Dict[str, Any], prefix: str = ""):
        for name, value in g.items():
            if isinstance(value, list):
                # Files in this directory
                for file_path in value:
                    display_path = str(Path(file_path).relative_to(base_dir))
                    is_disabled = display_path.endswith(".disabled")
                    test_name = (
                        f"{prefix}{name}/{display_path}" if prefix else display_path
                    )
                    test_cases.append((test_name, file_path, is_disabled))
            else:
                # Nested directory
                new_prefix = f"{prefix}{name}/" if prefix else f"{name}/"
                collect_files(value, new_prefix)

    collect_files(group)
    return test_cases


class TestSchemaValidation:
    """Test class for schema validation."""

    def setup_class(self):
        """Setup test paths."""
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.examples_dir = self.project_root / "reference" / "examples"
        self.counterexamples_dir = self.project_root / "reference" / "counterexamples"

    def test_examples_exist(self):
        """Verify that examples directory exists."""
        assert self.examples_dir.exists(), (
            f"Examples directory not found: {self.examples_dir}"
        )

    def test_counterexamples_exist(self):
        """Verify that counterexamples directory exists."""
        assert self.counterexamples_dir.exists(), (
            f"Counterexamples directory not found: {self.counterexamples_dir}"
        )


def pytest_generate_tests(metafunc):
    """Generate parameterized tests for examples and counterexamples."""
    if "example_file" in metafunc.fixturenames:
        # Generate tests for examples (should pass validation)
        project_root = Path(__file__).parent.parent.parent.parent
        examples_dir = project_root / "reference" / "examples"

        if examples_dir.exists():
            example_files = list(walk_directory(examples_dir))
            grouped_examples = group_files_by_directory(example_files, examples_dir)
            test_cases = create_test_cases(
                grouped_examples, examples_dir, is_counterexample=False
            )

            # Filter test cases based on disabled status
            enabled_cases = [
                (name, path) for name, path, disabled in test_cases if not disabled
            ]
            disabled_cases = [
                (name, path) for name, path, disabled in test_cases if disabled
            ]

            # Add mark for disabled tests
            test_ids = [case[0] for case in enabled_cases]
            test_values = [case[1] for case in enabled_cases]

            metafunc.parametrize("example_file", test_values, ids=test_ids)

            # Create skipped tests for disabled files
            if disabled_cases:
                # These will be handled separately with pytest.mark.skip
                pass

    elif "counterexample_file" in metafunc.fixturenames:
        # Generate tests for counterexamples (should fail validation)
        project_root = Path(__file__).parent.parent.parent.parent
        counterexamples_dir = project_root / "reference" / "counterexamples"

        if counterexamples_dir.exists():
            counterexample_files = list(walk_directory(counterexamples_dir))
            grouped_counterexamples = group_files_by_directory(
                counterexample_files, counterexamples_dir
            )
            test_cases = create_test_cases(
                grouped_counterexamples, counterexamples_dir, is_counterexample=True
            )

            # Filter test cases based on disabled status
            enabled_cases = [
                (name, path) for name, path, disabled in test_cases if not disabled
            ]

            test_ids = [case[0] for case in enabled_cases]
            test_values = [case[1] for case in enabled_cases]

            metafunc.parametrize("counterexample_file", test_values, ids=test_ids)


def test_example_validation_geojson(example_file):
    """Test that examples pass validation with GeoJSON input format."""
    test_feature = convert_to_geojson_format(load_feature(example_file))

    is_valid = False
    error_msg = None
    try:
        parsed_feature = parse_feature(test_feature)
        is_valid = True
    except Exception as e:
        error_msg = e

    assert is_valid, (
        f"Example failed validation (geojson): {example_file}\nError: {error_msg}"
    )

    # If validation passed and we have a parsed feature, compare with GeoJSON format
    if parsed_feature is not None:
        # Parsed feature should be in GeoJSON format, so compare directly
        is_equal, diff_report = deep_compare_dicts(test_feature, parsed_feature)
        assert is_equal, (
            f"Parsed feature differs from original (geojson): {example_file}\n"
            f"Differences:\n{diff_report}"
        )


def test_example_validation_flat(example_file):
    """Test that examples pass validation with flat/Parquet-style input."""
    flat_feature = load_feature(example_file)  # Load as flat (authoritative)
    test_feature = flat_feature  # Use flat format directly

    is_valid = False
    error_msg = None
    try:
        parsed_feature = parse_feature(test_feature)
        is_valid = True
    except Exception as e:
        error_msg = e

    assert is_valid, (
        f"Example failed validation (flat): {example_file}\nError: {error_msg}"
    )

    # If validation passed and we have a parsed feature, compare with GeoJSON format
    if parsed_feature is not None:
        # Parsed feature should be in GeoJSON format, so compare with GeoJSON variant
        expected_geojson = convert_to_geojson_format(flat_feature)
        is_equal, diff_report = deep_compare_dicts(expected_geojson, parsed_feature)
        assert is_equal, (
            f"Parsed feature differs from expected (flat): {example_file}\n"
            f"Differences:\n{diff_report}"
        )


def test_example_validation_shapely(example_file):
    """Test that examples pass validation with Shapely geometry input."""
    flat_feature = load_feature(example_file)  # Load as flat (authoritative)
    test_feature = create_shapely_variant(flat_feature)

    is_valid = False
    error_msg = None
    try:
        parsed_feature = parse_feature(test_feature)
        is_valid = True
    except Exception as e:
        error_msg = e

    assert is_valid, (
        f"Example failed validation (shapely): {example_file}\nError: {error_msg}"
    )

    # If validation passed and we have a parsed feature, compare with GeoJSON format
    if parsed_feature is not None:
        # Parsed feature should be in GeoJSON format, so compare with GeoJSON variant
        expected_geojson = convert_to_geojson_format(flat_feature)
        is_equal, diff_report = deep_compare_dicts(expected_geojson, parsed_feature)
        assert is_equal, (
            f"Parsed feature differs from expected (shapely): {example_file}\n"
            f"Differences:\n{diff_report}"
        )


def test_counterexample_validation_geojson(counterexample_file):
    """Test that counterexamples fail validation with GeoJSON input format."""
    flat_feature = load_feature(counterexample_file)  # Load as flat (authoritative)
    test_feature = convert_to_geojson_format(flat_feature)  # Convert to GeoJSON format

    is_valid = False
    try:
        parse_feature(test_feature)
        is_valid = True
    except Exception:
        pass

    assert not is_valid, (
        f"Counterexample should have failed validation (geojson): {counterexample_file}"
    )


def test_counterexample_validation_shapely(counterexample_file):
    """Test that counterexamples fail validation with Shapely geometry input."""
    flat_feature = load_feature(counterexample_file)  # Load as flat (authoritative)
    test_feature = create_shapely_variant(flat_feature)

    is_valid = False
    try:
        parse_feature(test_feature)
        is_valid = True
    except Exception:
        pass

    assert not is_valid, (
        f"Counterexample should have failed validation (shapely): {counterexample_file}"
    )


def test_example_validation_wkb(example_file):
    """Test that examples pass validation with WKB geometry input."""
    flat_feature = load_feature(example_file)  # Load as flat (authoritative)
    test_feature = create_wkb_variant(flat_feature)

    is_valid = False
    error_msg = None
    try:
        parsed_feature = parse_feature(test_feature)
        is_valid = True
    except Exception as e:
        error_msg = e

    assert is_valid, (
        f"Example failed validation (wkb): {example_file}\nError: {error_msg}"
    )

    # If validation passed and we have a parsed feature, compare with GeoJSON format
    if parsed_feature is not None:
        # Parsed feature should be in GeoJSON format, so compare with GeoJSON variant
        expected_geojson = convert_to_geojson_format(flat_feature)
        is_equal, diff_report = deep_compare_dicts(expected_geojson, parsed_feature)
        assert is_equal, (
            f"Parsed feature differs from expected (wkb): {example_file}\n"
            f"Differences:\n{diff_report}"
        )


def test_counterexample_validation_wkb(counterexample_file):
    """Test that counterexamples fail validation with WKB geometry input."""
    flat_feature = load_feature(counterexample_file)  # Load as flat (authoritative)
    test_feature = create_wkb_variant(flat_feature)

    is_valid = False
    try:
        parse_feature(test_feature)
        is_valid = True
    except Exception:
        pass

    assert not is_valid, (
        f"Counterexample should have failed validation (wkb): {counterexample_file}"
    )


def test_example_validation_wkt(example_file):
    """Test that examples pass validation with WKT geometry input."""
    flat_feature = load_feature(example_file)  # Load as flat (authoritative)
    test_feature = create_wkt_variant(flat_feature)

    is_valid = False
    error_msg = None
    try:
        parsed_feature = parse_feature(test_feature)
        is_valid = True
    except Exception as e:
        error_msg = e

    assert is_valid, (
        f"Example failed validation (wkt): {example_file}\nError: {error_msg}"
    )

    # If validation passed and we have a parsed feature, compare with GeoJSON format
    if parsed_feature is not None:
        # Parsed feature should be in GeoJSON format, so compare with GeoJSON variant
        expected_geojson = convert_to_geojson_format(flat_feature)
        is_equal, diff_report = deep_compare_dicts(expected_geojson, parsed_feature)
        assert is_equal, (
            f"Parsed feature differs from expected (wkt): {example_file}\n"
            f"Differences:\n{diff_report}"
        )


def test_counterexample_validation_wkt(counterexample_file):
    """Test that counterexamples fail validation with WKT geometry input."""
    flat_feature = load_feature(counterexample_file)  # Load as flat (authoritative)
    test_feature = create_wkt_variant(flat_feature)

    is_valid = False
    try:
        parse_feature(test_feature)
        is_valid = True
    except Exception:
        pass

    assert not is_valid, (
        f"Counterexample should have failed validation (wkt): {counterexample_file}"
    )


def test_example_serialization_modes(example_file):
    """Test that serialization modes produce expected formats."""
    flat_feature = load_feature(example_file)

    # Test Python mode (should return flattened structure)
    try:
        python_output = parse_feature(flat_feature, mode="python")
    except Exception as e:
        pytest.fail(f"Python mode parsing failed: {e}")

    # Test JSON mode (should return GeoJSON structure)
    try:
        json_output = parse_feature(flat_feature, mode="json")
    except Exception as e:
        pytest.fail(f"JSON mode parsing failed: {e}")

    # Assertions for Python output (flattened)
    assert "properties" not in python_output, (
        f"Python mode should not have 'properties' key: {example_file}"
    )
    assert "id" in python_output, (
        f"Python mode should have 'id' at top level: {example_file}"
    )
    assert "geometry" in python_output, (
        f"Python mode should have 'geometry' at top level: {example_file}"
    )
    assert "theme" in python_output, (
        f"Python mode should have 'theme' at top level: {example_file}"
    )
    assert "type" in python_output, (
        f"Python mode should have 'type' at top level: {example_file}"
    )

    # Assertions for JSON output (GeoJSON)
    assert json_output.get("type") == "Feature", (
        f"JSON mode should have GeoJSON 'type': {example_file}"
    )
    assert "properties" in json_output, (
        f"JSON mode should have 'properties' key: {example_file}"
    )
    assert "id" in json_output, (
        f"JSON mode should have 'id' at top level: {example_file}"
    )
    assert "geometry" in json_output, (
        f"JSON mode should have 'geometry' at top level: {example_file}"
    )

    # Properties should contain theme and type
    properties = json_output["properties"]
    assert "theme" in properties, (
        f"JSON mode properties should contain 'theme': {example_file}"
    )
    assert "type" in properties, (
        f"JSON mode properties should contain 'type': {example_file}"
    )

    # Cross-validation: outputs should contain same data, just structured differently
    flattened_from_json = {
        "id": json_output["id"],
        "geometry": json_output["geometry"],
        **json_output["properties"],
    }

    # Handle geometry comparison - Python mode keeps Geometry objects, JSON mode converts to dict
    python_output_for_comparison = python_output.copy()
    if "geometry" in python_output_for_comparison:
        geom = python_output_for_comparison["geometry"]
        if hasattr(geom, "to_geo_json"):
            python_output_for_comparison["geometry"] = geom.to_geo_json()

    # Normalize both outputs to JSON for comparison (handles tuple/list differences)
    import json

    python_json_normalized = json.loads(
        json.dumps(python_output_for_comparison, default=str)
    )
    flattened_json_normalized = json.loads(json.dumps(flattened_from_json, default=str))

    is_equal, diff_report = deep_compare_dicts(
        python_json_normalized, flattened_json_normalized
    )
    assert is_equal, (
        f"Python and flattened JSON outputs should match: {example_file}\n"
        f"Differences:\n{diff_report}"
    )


def test_example_roundtrip_consistency(example_file):
    """Test that Python->JSON->Python roundtrip preserves data."""
    flat_feature = load_feature(example_file)

    try:
        # Parse in Python mode
        python_output = parse_feature(flat_feature, mode="python")

        # Convert to JSON mode (which is parseable) then back to Python mode
        json_output = parse_feature(flat_feature, mode="json")
        roundtrip_output = parse_feature(json_output, mode="python")

        # Normalize both for comparison (handle Geometry objects)
        import json

        python_normalized = python_output.copy()
        if "geometry" in python_normalized:
            geom = python_normalized["geometry"]
            if hasattr(geom, "to_geo_json"):
                python_normalized["geometry"] = geom.to_geo_json()
        python_normalized = json.loads(json.dumps(python_normalized, default=str))

        roundtrip_normalized = roundtrip_output.copy()
        if "geometry" in roundtrip_normalized:
            geom = roundtrip_normalized["geometry"]
            if hasattr(geom, "to_geo_json"):
                roundtrip_normalized["geometry"] = geom.to_geo_json()
        roundtrip_normalized = json.loads(json.dumps(roundtrip_normalized, default=str))

        # Should be identical
        is_equal, diff_report = deep_compare_dicts(
            python_normalized, roundtrip_normalized
        )
        assert is_equal, (
            f"Python mode roundtrip should preserve data: {example_file}\n"
            f"Differences:\n{diff_report}"
        )

    except Exception as e:
        pytest.fail(f"Roundtrip test failed: {e}")


def test_example_cross_mode_consistency(example_file):
    """Test that GeoJSON->flatten and flatten->GeoJSON produce consistent results."""
    flat_feature = load_feature(example_file)
    geojson_feature = convert_to_geojson_format(flat_feature)

    try:
        # Parse flattened input in both modes
        python_from_flat = parse_feature(flat_feature, mode="python")
        json_from_flat = parse_feature(flat_feature, mode="json")

        # Parse GeoJSON input in both modes
        python_from_geojson = parse_feature(geojson_feature, mode="python")
        json_from_geojson = parse_feature(geojson_feature, mode="json")

        # Results should be identical regardless of input format
        is_equal, diff_report = deep_compare_dicts(
            python_from_flat, python_from_geojson
        )
        assert is_equal, (
            f"Python mode should produce same result from flat/GeoJSON input: {example_file}\n"
            f"Differences:\n{diff_report}"
        )

        is_equal, diff_report = deep_compare_dicts(json_from_flat, json_from_geojson)
        assert is_equal, (
            f"JSON mode should produce same result from flat/GeoJSON input: {example_file}\n"
            f"Differences:\n{diff_report}"
        )

    except Exception as e:
        pytest.fail(f"Cross-mode consistency test failed: {e}")
