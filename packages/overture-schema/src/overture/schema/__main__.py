"""JSON Schema generation command for Overture Maps schemas."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from overture.schema.core import json_schema
from overture.schema.core.discovery import (
    discover_models,
    get_registered_model,
)


def list_theme_types() -> list[tuple[str, str]]:
    """List all available theme-type combinations."""

    return list(discover_models().keys())


def generate_specific_schema(theme: str, feature_type: str) -> dict[str, Any] | None:
    """Generate JSON schema for a specific theme-type combination."""

    model_class = get_registered_model(theme, feature_type)
    if model_class is None:
        return None

    return json_schema(model_class)


def main() -> None:
    """Main entry point for the JSON Schema generation command."""
    parser = argparse.ArgumentParser(description="Generate Overture Maps JSON Schemas")
    # TODO now that we support generating a unified schema, introduce the ability to do that
    parser.add_argument("--theme", help="Generate schema for specific theme (required)")
    parser.add_argument(
        "--type", help="Generate schema for specific feature type (required)"
    )
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
            for theme, feature_type in sorted(list_theme_types()):
                print(f"  {theme}:{feature_type}")
            return

        if args.output_dir:
            # Generate all schemas as separate files
            output_dir = Path(args.output_dir)
            output_dir.mkdir(exist_ok=True)

            for theme, feature_type in list_theme_types():
                schema = generate_specific_schema(theme, feature_type)
                if schema:
                    filename = f"overture-schema-{theme}-{feature_type}.json"
                    filepath = output_dir / filename
                    with open(filepath, "w") as f:
                        json.dump(schema, f, indent=2, sort_keys=True)
                    print(f"Generated {filepath}")
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

        # Require theme and type arguments - no monolithic schema support
        print(
            "ERROR: You must specify --theme and --type arguments, or use --list-types or --output-dir",
            file=sys.stderr,
        )
        print("\nMonolithic schema generation is no longer supported.", file=sys.stderr)
        print(
            "Use --list-types to see available theme-type combinations.",
            file=sys.stderr,
        )
        print(
            "Use --output-dir to generate all schemas as separate files.",
            file=sys.stderr,
        )
        sys.exit(1)

    except Exception as e:
        print(f"Error generating JSON schemas: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
