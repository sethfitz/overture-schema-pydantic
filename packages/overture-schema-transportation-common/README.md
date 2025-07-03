# Overture Schema Transportation Common

Common structures, enums, and validation logic shared across all transportation-related Overture Map types.

This package contains:
- Transportation segment subtypes (SegmentSubtype)
- Road and rail classification enums (RoadClass, RailClass)
- Speed limit and access restriction models
- Surface material enums and rules
- Connector and route reference models
- Shared validation utilities

## Usage

```python
from overture.schema.transportation.common import SegmentSubtype, RoadClass, SpeedLimitRule
```

This package is designed to be imported by transportation-specific type packages (segment, connector) and theme packages, breaking circular dependencies.