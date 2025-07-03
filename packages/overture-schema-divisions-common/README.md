# Overture Schema Divisions Common

Common structures, enums, and validation logic shared across all divisions-related Overture Map types.

This package contains:
- Administrative hierarchy enums (PlaceType)
- Division classification enums (DivisionClass)
- Political perspective models (Perspectives)
- Hierarchy validation models (HierarchyItem)
- Local norms models (Norms)
- Common validation utilities

## Usage

```python
from overture.schema.divisions.common import PlaceType, DivisionClass, Perspectives
```

This package is designed to be imported by division-specific type packages (division, division_area, division_boundary) and theme packages, breaking circular dependencies.