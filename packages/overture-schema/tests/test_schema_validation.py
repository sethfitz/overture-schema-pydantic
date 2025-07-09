"""
Pytest-based test harness for validating Pydantic schemas against examples and counterexamples.
Similar to the TypeScript version but using pytest, with support for .disabled extensions.
"""

from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple

import overture.schema.addresses.address.models  # noqa: F401
import overture.schema.base.bathymetry.models  # noqa: F401
import overture.schema.base.infrastructure.models  # noqa: F401
import overture.schema.base.land.models  # noqa: F401
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
from yamlcore import CoreLoader


def load_feature(file_path: str) -> Dict[str, Any]:
    """Load a feature from JSON or YAML file."""
    with open(file_path, encoding="utf-8") as f:
        # use a YAML-1.2-compliant (which dropped support for yes/no boolean values) Loader
        return yaml.load(f, Loader=CoreLoader)


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


def test_example_validation(example_file):
    """Test that examples pass validation and compare parsed result with original."""
    original_feature = load_feature(example_file)

    is_valid = False
    error_msg = None
    try:
        parsed_feature = parse_feature(original_feature)
        is_valid = True
    except Exception as e:
        error_msg = e

    assert is_valid, f"Example failed validation: {example_file}\nError: {error_msg}"

    # If validation passed and we have a parsed feature, compare with original
    if parsed_feature is not None:
        is_equal, diff_report = deep_compare_dicts(original_feature, parsed_feature)
        assert is_equal, (
            f"Parsed feature differs from original: {example_file}\n"
            f"Differences:\n{diff_report}"
        )


def test_counterexample_validation(counterexample_file):
    """Test that counterexamples fail validation."""
    feature = load_feature(counterexample_file)

    is_valid = False
    try:
        parse_feature(feature)
        is_valid = True
    except Exception as e:
        pass

    assert not is_valid, (
        f"Counterexample should have failed validation: {counterexample_file}"
    )


# Additional helper functions for disabled test handling


def get_disabled_test_cases():
    """Get all disabled test cases for reporting."""
    project_root = Path(__file__).parent.parent.parent.parent

    disabled_examples = []
    disabled_counterexamples = []

    # Examples
    examples_dir = project_root / "reference" / "examples"
    if examples_dir.exists():
        example_files = list(walk_directory(examples_dir))
        grouped_examples = group_files_by_directory(example_files, examples_dir)
        example_test_cases = create_test_cases(
            grouped_examples, examples_dir, is_counterexample=False
        )
        disabled_examples = [
            (name, path) for name, path, disabled in example_test_cases if disabled
        ]

    # Counterexamples
    counterexamples_dir = project_root / "reference" / "counterexamples"
    if counterexamples_dir.exists():
        counterexample_files = list(walk_directory(counterexamples_dir))
        grouped_counterexamples = group_files_by_directory(
            counterexample_files, counterexamples_dir
        )
        counterexample_test_cases = create_test_cases(
            grouped_counterexamples, counterexamples_dir, is_counterexample=True
        )
        disabled_counterexamples = [
            (name, path)
            for name, path, disabled in counterexample_test_cases
            if disabled
        ]

    return disabled_examples, disabled_counterexamples


@pytest.mark.skip(reason="Disabled test files")
class TestDisabledFiles:
    """Tests for disabled files - these are skipped by default."""

    def test_report_disabled_files(self):
        """Report on disabled test files."""
        disabled_examples, disabled_counterexamples = get_disabled_test_cases()

        print(f"\nDisabled Examples ({len(disabled_examples)}):")
        for name, _path in disabled_examples:
            print(f"  - {name}")

        print(f"\nDisabled Counterexamples ({len(disabled_counterexamples)}):")
        for name, _path in disabled_counterexamples:
            print(f"  - {name}")
