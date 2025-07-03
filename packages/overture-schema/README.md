# overture-schema

Complete Overture Maps schema collection with all themes and types.

This meta-package provides a convenient way to install all Overture Maps Pydantic schemas at once. It includes all theme packages and their dependencies.

## Installation

```bash
pip install overture-schema
```

This will install all theme packages:
- `overture-schema-base-theme` - Base theme (infrastructure, land, water, bathymetry)
- `overture-schema-addresses-theme` - Address theme
- `overture-schema-buildings-theme` - Buildings theme  
- `overture-schema-divisions-theme` - Divisions theme
- `overture-schema-places-theme` - Places theme
- `overture-schema-transportation-theme` - Transportation theme

## Usage

Import specific schemas from their respective theme packages:

```python
# Base theme
from overture.schema.base.infrastructure import InfrastructureFeature
from overture.schema.base.land import LandFeature
from overture.schema.base.water import WaterFeature
from overture.schema.base.bathymetry import BathymetryFeature

# Buildings theme
from overture.schema.buildings.building import BuildingFeature
from overture.schema.buildings.building_part import BuildingPartFeature

# Transportation theme
from overture.schema.transportation.segment import SegmentFeature
from overture.schema.transportation.connector import ConnectorFeature

# Places theme
from overture.schema.places.place import PlaceFeature

# Divisions theme
from overture.schema.divisions.division import DivisionFeature
from overture.schema.divisions.division_area import DivisionAreaFeature
from overture.schema.divisions.division_boundary import DivisionBoundaryFeature

# Addresses theme
from overture.schema.addresses.address import AddressFeature
```

For more detailed usage examples, see the individual theme package documentation.

## Architecture

This package follows a multi-package architecture where each theme and type is packaged separately for modularity. The `overture-schema` package serves as a convenience meta-package that includes all themes.

Individual packages can also be installed separately if you only need specific schemas:

```bash
# Install only transportation schemas
pip install overture-schema-transportation-theme

# Install only buildings schemas  
pip install overture-schema-buildings-theme
```