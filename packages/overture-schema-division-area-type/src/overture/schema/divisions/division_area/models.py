"""Division area models for Overture Maps divisions theme."""

from typing import List, Optional

from pydantic import Field, field_validator

from overture.schema.core.base import (
    OvertureFeature,
    OvertureFeatureProperties,
    register_model,
)
from overture.schema.core.common import (
    AdvancedSourceItem,
    NamesContainer,
)
from overture.schema.divisions.common.models import (
    AreaBoundaryClass,
    PlaceType,
)


class DivisionAreaProperties(OvertureFeatureProperties):
    """Properties specific to division area features."""

    # Required properties
    subtype: PlaceType = Field(..., description="Administrative level")
    class_: AreaBoundaryClass = Field(
        ..., alias="class", description="Area class (land/maritime)"
    )
    division_id: str = Field(
        ...,
        min_length=1,
        pattern=r"^(\S.*)?\S$",
        description="Referenced division ID (no leading/trailing whitespace)",
    )

    # Geographic context
    country: str = Field(
        ..., pattern=r"^[A-Z]{2}$", description="ISO 3166-1 alpha-2 country code"
    )
    region: Optional[str] = Field(
        None, pattern=r"^[A-Z]{2}-[A-Z0-9]{1,3}$", description="ISO 3166-2 region code"
    )

    # Territorial designation (exclusive or) - strict boolean validation
    is_land: Optional[bool] = Field(
        None, description="Land area designation", strict=True
    )
    is_territorial: Optional[bool] = Field(
        None, description="Territorial area designation", strict=True
    )

    # Complex containers
    names: Optional[NamesContainer] = Field(None, description="Multilingual names")
    sources: Optional[List[AdvancedSourceItem]] = Field(
        None, min_length=1, description="Advanced source information"
    )

    @field_validator("theme")
    @classmethod
    def validate_theme(cls, v):
        if v != "divisions":
            raise ValueError("Division area theme must be 'divisions'")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v != "division_area":
            raise ValueError("Division area type must be 'division_area'")
        return v

    @field_validator("is_territorial")
    @classmethod
    def validate_territorial_exclusive(cls, v, info):
        """Ensure is_land and is_territorial are mutually exclusive."""
        if v is not None and hasattr(info, "data") and "is_land" in info.data:
            is_land = info.data["is_land"]
            if is_land is not None and v and is_land:
                raise ValueError("is_land and is_territorial cannot both be true")
        return v


class DivisionArea(OvertureFeature):
    """Division area feature model."""

    properties: DivisionAreaProperties = Field(
        ..., description="Division area feature properties"
    )

    @field_validator("geometry")
    @classmethod
    def validate_geometry_type(cls, v):
        """Division areas must have Polygon or MultiPolygon geometry."""
        # Call parent validation first
        super().validate_geometry_structure(v)

        geom_type = v.get("type")
        if geom_type not in ["Polygon", "MultiPolygon"]:
            raise ValueError(
                f"Division area geometry must be Polygon or MultiPolygon, got {geom_type}"
            )

        # Validate coordinates structure
        if "coordinates" in v:
            coords = v["coordinates"]
            if not isinstance(coords, list):
                raise ValueError("Coordinates must be an array")

            # Validate structure based on geometry type
            if geom_type == "Polygon":
                # Polygon coordinates: [[[x,y], [x,y], ...], [[x,y], [x,y], ...]]
                # Must be array of linear rings (each ring is array of positions)
                if not coords:
                    raise ValueError("Polygon coordinates cannot be empty")

                for ring_idx, ring in enumerate(coords):
                    if not isinstance(ring, list):
                        raise ValueError(
                            f"Polygon ring {ring_idx} must be an array, got {type(ring).__name__}"
                        )

                    for pos_idx, position in enumerate(ring):
                        if not isinstance(position, list):
                            raise ValueError(
                                f"Position at ring {ring_idx}, index {pos_idx} must be an array, got {type(position).__name__}"
                            )

                        if len(position) < 2:
                            raise ValueError(
                                f"Position at ring {ring_idx}, index {pos_idx} must have at least 2 coordinates"
                            )

                        for coord_idx, coord in enumerate(position):
                            if not isinstance(coord, (int, float)):
                                raise ValueError(
                                    f"Coordinate at ring {ring_idx}, position {pos_idx}, index {coord_idx} must be a number, got {type(coord).__name__}"
                                )

            elif geom_type == "MultiPolygon":
                # MultiPolygon coordinates: [[[[x,y], [x,y], ...]], [[[x,y], [x,y], ...]]]
                # Array of polygons, each polygon is array of linear rings
                if not coords:
                    raise ValueError("MultiPolygon coordinates cannot be empty")

                for poly_idx, polygon in enumerate(coords):
                    if not isinstance(polygon, list):
                        raise ValueError(
                            f"MultiPolygon polygon {poly_idx} must be an array, got {type(polygon).__name__}"
                        )

                    for ring_idx, ring in enumerate(polygon):
                        if not isinstance(ring, list):
                            raise ValueError(
                                f"MultiPolygon polygon {poly_idx}, ring {ring_idx} must be an array, got {type(ring).__name__}"
                            )

                        for pos_idx, position in enumerate(ring):
                            if not isinstance(position, list):
                                raise ValueError(
                                    f"Position at polygon {poly_idx}, ring {ring_idx}, index {pos_idx} must be an array, got {type(position).__name__}"
                                )

                            if len(position) < 2:
                                raise ValueError(
                                    f"Position at polygon {poly_idx}, ring {ring_idx}, index {pos_idx} must have at least 2 coordinates"
                                )

                            for coord_idx, coord in enumerate(position):
                                if not isinstance(coord, (int, float)):
                                    raise ValueError(
                                        f"Coordinate at polygon {poly_idx}, ring {ring_idx}, position {pos_idx}, index {coord_idx} must be a number, got {type(coord).__name__}"
                                    )

        return v


# Register the model
register_model("divisions", "division_area", DivisionArea)
