"""JSON Schema generation command for Overture Maps schemas."""

import json
import sys
from typing import Dict, Any, Type
import importlib.util
import pkgutil
from pathlib import Path

from pydantic import BaseModel

# Import all model packages to trigger registration
try:
    import overture.schema.addresses.address.models
    import overture.schema.base.bathymetry.models
    import overture.schema.base.infrastructure.models
    import overture.schema.base.land.models
    import overture.schema.base.water.models
    import overture.schema.buildings.building.models
    import overture.schema.buildings.building_part.models
    import overture.schema.divisions.division.models
    import overture.schema.divisions.division_area.models
    import overture.schema.divisions.division_boundary.models
    import overture.schema.places.place.models
    import overture.schema.transportation.connector.models
    import overture.schema.transportation.segment.models
except ImportError as e:
    print(f"Warning: Could not import some model packages: {e}", file=sys.stderr)

from overture.schema.core.base import _FEATURE_MODELS


def generate_json_schemas() -> Dict[str, Any]:
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


def main():
    """Main entry point for the JSON Schema generation command."""
    try:
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
