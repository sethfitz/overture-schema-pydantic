# Overture Schema

Pydantic schemas for Overture Maps data structures.

## Project Structure

This project uses a multi-package workspace architecture with theme-based namespaces and type-specific packages:

```
packages/
├── overture-schema/                   # Main entrypoint package (aggregates all types)
├── overture-schema-core/              # Base classes and common structures
├── overture-schema-segment-type/      # Transportation segments
├── overture-schema-connector-type/    # Transportation connectors
├── overture-schema-building-type/     # Building features
├── overture-schema-place-type/        # Place features
└── ...                               # Other type-specific packages
```

The `overture-schema` package serves as the main entrypoint and aggregates all type-specific packages. For extensions, depend on specific packages directly:

```python
# Main usage - includes all types
from overture.schema.transportation.segment import Segment

# Extension development - depend on specific packages only
from overture.schema.core.base import OvertureFeature
from overture.schema.transportation.segment import Segment
```

## Schema Extension

The library is designed to support data producer extensions through:

### New Columns

```python
from overture.schema.buildings.building import Building
from pydantic import Field

class ExtendedBuilding(Building):
    door_color: str = Field(description="Color of the building's front door")
    security_level: int = Field(ge=1, le=5, description="Security clearance level")
```

### New Types

```python
from overture.schema.core.base import OvertureFeature
from overture.schema.places.place import Place
from pydantic import Field
from typing import Literal

class EVCharger(OvertureFeature):
    """Electric vehicle charging station with specialized attributes"""
    type: Literal["ev_charger"] = "ev_charger"
    connector_types: list[str] = Field(description="Available connector types (CCS, CHAdeMO, etc.)")
    max_power_kw: float = Field(description="Maximum charging power in kilowatts")
    network_operator: str | None = Field(default=None, description="Charging network operator")
    pricing_model: str | None = Field(default=None, description="Pricing structure")
    payment_methods: list[str] = Field(default_factory=list, description="Accepted payment methods")
```

### Linear Referencing Extensions

```python
from overture.schema.transportation.segment import Segment
from overture.schema.core.base import LinearReferencedEvent
from pydantic import BaseModel, Field
from typing import Literal
from datetime import time

class TimeSpan(BaseModel):
    """Time-based restriction following CurbLR specification"""
    days_of_week: list[str] = Field(description="Days when restriction applies")
    time_of_day_start: time | None = Field(default=None, description="Start time")
    time_of_day_end: time | None = Field(default=None, description="End time")
    designated_period: str | None = Field(default=None, description="Named time period (school_days, snow_emergency)")

class PaymentTerms(BaseModel):
    """Payment requirements for curb usage"""
    rate: float | None = Field(default=None, description="Cost per unit time")
    rate_unit: str | None = Field(default=None, description="Unit of time for rate (hour, day)")
    methods: list[str] = Field(default_factory=list, description="Accepted payment methods")

class CurbRestriction(LinearReferencedEvent):
    """Curb usage restrictions following CurbLR specification"""
    type: Literal["curb_restriction"] = "curb_restriction"
    rule: str = Field(description="Type of regulation (no_parking, loading_zone, etc.)")
    user_classes: list[str] = Field(default_factory=list, description="Vehicle types or user groups")
    time_spans: list[TimeSpan] = Field(default_factory=list, description="When restriction applies")
    payment: PaymentTerms | None = Field(default=None, description="Payment requirements")
    priority: int = Field(default=1, description="Priority for overlapping regulations")
    max_stay_minutes: int | None = Field(default=None, description="Maximum stay duration")
```

## Tooling: Hatch + uv

This project uses [Hatch](https://hatch.pypa.io/) for project management and [uv](https://github.com/astral-sh/uv) for fast dependency resolution.

### Why Hatch?

- **Multi-package workspaces**: Manages multiple related packages in one repository
- **Modern build standards**: Built around [PEP 517](https://peps.python.org/pep-0517/) (build system interface) and [PEP 518](https://peps.python.org/pep-0518/) (build system requirements)
- **Environment management**: Built-in test matrix and environment handling
- **Publishing workflow**: Streamlined process for publishing multiple packages

### Why uv?

- **Performance**: Rust-based package installer, significantly faster than pip
- **Compatibility**: Drop-in replacement for pip/pip-tools
- **Workspace support**: Handles multi-package projects with local dependencies

### Integration

- **Hatch** manages the build system (`hatchling` backend) and project structure
- **uv** handles dependency resolution and installation
- **Workspace configuration** enables local development with editable installs

## Development

```bash
# Install dependencies for entire workspace
uv sync

# Install specific package in development mode
uv pip install -e packages/overture-schema-core

# Run tests across all packages
uv run pytest

# Run tests for specific package
uv run pytest packages/overture-schema-core

# Run linting and formatting
uv run ruff check .
uv run ruff format .

# Type checking
uv run mypy packages/

# Build specific package
uv run python -m build packages/overture-schema-core
```

## Multi-Package Workflow

The workspace configuration in `pyproject.toml` enables seamless development:

```toml
[tool.uv.sources]
overture-schema-core = { path = "packages/overture-schema-core", editable = true }
overture-schema-segment-type = { path = "packages/overture-schema-segment-type", editable = true }
# ... other packages
```

This provides:

- **Local development**: Changes to one package immediately available to others
- **Dependency management**: Automatic resolution of inter-package dependencies  
- **Unified testing**: Run tests across all packages while respecting dependencies
