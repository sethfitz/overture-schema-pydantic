"""Building feature models for Overture Maps buildings theme."""

from __future__ import annotations

from typing import Annotated, Optional

from pydantic import Field

from overture.schema.buildings.common import (
    BuildingClass,
    BuildingSubtype,
    FacadeMaterial,
    RoofMaterial,
    RoofOrientation,
    RoofShape,
)
from overture.schema.core.base import OvertureFeature, register_model
from overture.schema.core.common import (
    AddressContainer,
    NamesContainer,
)
from overture.schema.core.geometry import Geometry, GeometryTypeConstraint
from overture.schema.validation import (
    HexColor,
    theme_literal,
    type_literal,
)


class Building(OvertureFeature):
    """Building feature model."""

    # Override theme and type with constraint-based validation
    theme: theme_literal("buildings") = Field("buildings", description="Feature theme")
    type: type_literal("building") = Field("building", description="Feature type")

    # Required properties
    subtype: Optional[BuildingSubtype] = Field(None, description="Building subtype")

    # Optional complex containers
    names: Optional[NamesContainer] = Field(None, description="Multilingual names")
    address: Optional[AddressContainer] = Field(None, description="Address information")

    # Optional numeric properties
    height: Optional[float] = Field(
        None, gt=0, description="Height of the building in meters"
    )
    num_floors: Optional[int] = Field(
        None, gt=0, description="Number of above-ground floors"
    )
    num_floors_underground: Optional[int] = Field(
        None, gt=0, description="Number of below-ground floors"
    )
    min_height: Optional[float] = Field(
        None, description="Building bottom height in meters"
    )
    min_floor: Optional[int] = Field(
        None, gt=0, description="Start floor if building is floating"
    )
    roof_height: Optional[float] = Field(None, description="Roof height in meters")
    roof_direction: Optional[float] = Field(
        None, ge=0, lt=360, description="Roof bearing in degrees"
    )
    level: Optional[int] = Field(None, description="Z-order level")

    # Optional boolean properties
    has_parts: Optional[bool] = Field(None, description="Building has parts")
    is_underground: Optional[bool] = Field(
        None, description="Entire building is below ground"
    )

    # Optional classification properties
    building_class: Optional[BuildingClass] = Field(
        None, alias="class", description="Building class"
    )
    facade_material: Optional[FacadeMaterial] = Field(
        None, description="Facade material"
    )
    roof_material: Optional[RoofMaterial] = Field(None, description="Roof material")
    roof_shape: Optional[RoofShape] = Field(None, description="Roof shape")
    roof_orientation: Optional[RoofOrientation] = Field(
        None, description="Roof orientation"
    )

    # Optional color properties (hexadecimal strings)
    facade_color: Optional[HexColor] = Field(None, description="Facade color (hex)")
    roof_color: Optional[HexColor] = Field(None, description="Roof color (hex)")

    # Geometry
    geometry: Annotated[Geometry, GeometryTypeConstraint("Polygon", "MultiPolygon")] = (
        Field(..., description="Geometry (Polygon or MultiPolygon)")
    )


# Register Pydantic models when module is imported
register_model("buildings", "building", Building)
