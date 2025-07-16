"""JSON Schema generation command for Overture Maps schemas."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Import model packages to trigger registration
try:
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
except ImportError as e:
    print(f"Warning: Could not import some model packages: {e}", file=sys.stderr)

from overture.schema.core.base import _FEATURE_MODELS


def generate_json_schemas() -> dict[str, Any]:
    """Generate JSON schemas for all registered Pydantic models."""
    schemas = {}

    for (theme, feature_type), model_class in _FEATURE_MODELS.items():
        # Generate the JSON schema for this model
        json_schema = model_class.model_json_schema()

        # Create a hierarchical structure: theme -> type -> schema
        if theme not in schemas:
            schemas[theme] = {}

        schemas[theme][feature_type] = json_schema

    return schemas


def generate_specific_schema(theme: str, feature_type: str) -> dict[str, Any] | None:
    """Generate JSON schema for a specific theme-type combination."""
    if (theme, feature_type) not in _FEATURE_MODELS:
        return None

    model_class = _FEATURE_MODELS[(theme, feature_type)]
    return model_class.model_json_schema()


def main():
    """Main entry point for the JSON Schema generation command."""
    parser = argparse.ArgumentParser(description="Generate Overture Maps JSON Schemas")
    parser.add_argument("--theme", help="Generate schema for specific theme")
    parser.add_argument("--type", help="Generate schema for specific feature type")
    parser.add_argument(
        "--list-types",
        action="store_true",
        help="List all available theme-type combinations",
    )
    parser.add_argument(
        "--output-dir", help="Output directory for individual schema files"
    )

    args = parser.parse_args()

    try:
        if args.list_types:
            print("Available theme-type combinations:")
            for theme, feature_type in sorted(_FEATURE_MODELS.keys()):
                print(f"  {theme}:{feature_type}")
            return

        if args.theme and args.type:
            # Generate specific schema
            schema = generate_specific_schema(args.theme, args.type)
            if schema is None:
                print(f"No model found for {args.theme}:{args.type}", file=sys.stderr)
                sys.exit(1)

            output = json.dumps(schema, indent=2, sort_keys=True)
            print(output)
            return

        if args.output_dir:
            # Generate all schemas as separate files
            output_dir = Path(args.output_dir)
            output_dir.mkdir(exist_ok=True)

            for theme, feature_type in _FEATURE_MODELS.keys():
                schema = generate_specific_schema(theme, feature_type)
                if schema:
                    filename = f"overture-schema-{theme}-{feature_type}.json"
                    filepath = output_dir / filename
                    with open(filepath, "w") as f:
                        json.dump(schema, f, indent=2, sort_keys=True)
                    print(f"Generated {filepath}")
            return

        # Default: generate combined schema (backward compatibility)
        schemas = generate_json_schemas()

        if not schemas:
            print(
                "No registered models found. Make sure model packages are properly imported.",
                file=sys.stderr,
            )
            sys.exit(1)

        # Pretty print the JSON schemas
        output = json.dumps(schemas, indent=2, sort_keys=True)
        print(output)

    except Exception as e:
        print(f"Error generating JSON schemas: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
