# Overture Schema Bathymetry Type

Pydantic models for Overture Maps bathymetry features in the base theme.

## Features

- BathymetryFeature: Represents underwater depth measurements
- Validates required depth property (>= 0)
- Supports Polygon and MultiPolygon geometries
- Pure Pydantic validation with comprehensive error handling