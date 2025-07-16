"""Building part feature models for Overture Maps buildings theme."""

from typing import Annotated

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
from overture.schema.validation import HexColor, theme_literal, type_literal


class BuildingPart(OvertureFeature):
    """Building part feature model."""

    theme: theme_literal("buildings") = Field("buildings", description="Feature theme")
    type: type_literal("building_part") = Field(
        "building_part", description="Feature type"
    )

    # Required for building parts
    building_id: str = Field(..., min_length=1, description="Parent building ID")

    # Required properties
    subtype: BuildingSubtype | None = Field(None, description="Building subtype")

    # Optional complex containers
    names: NamesContainer | None = Field(None, description="Multilingual names")
    address: AddressContainer | None = Field(None, description="Address information")

    # Optional numeric properties
    height: float | None = Field(
        None, gt=0, description="Height of the building in meters"
    )
    num_floors: int | None = Field(
        None, gt=0, description="Number of above-ground floors"
    )
    num_floors_underground: int | None = Field(
        None, gt=0, description="Number of below-ground floors"
    )
    min_height: float | None = Field(
        None, description="Building bottom height in meters"
    )
    min_floor: int | None = Field(
        None, gt=0, description="Start floor if building is floating"
    )
    roof_height: float | None = Field(None, description="Roof height in meters")
    roof_direction: float | None = Field(
        None, ge=0, lt=360, description="Roof bearing in degrees"
    )
    level: int | None = Field(None, description="Z-order level")

    # Optional boolean properties
    has_parts: bool | None = Field(None, description="Building has parts")
    is_underground: bool | None = Field(
        None, description="Entire building is below ground"
    )

    # Optional classification properties
    building_class: BuildingClass | None = Field(
        None, alias="class", description="Building class"
    )
    facade_material: FacadeMaterial | None = Field(
        None, description="Facade material"
    )
    roof_material: RoofMaterial | None = Field(None, description="Roof material")
    roof_shape: RoofShape | None = Field(None, description="Roof shape")
    roof_orientation: RoofOrientation | None = Field(
        None, description="Roof orientation"
    )

    # Optional color properties (hexadecimal strings)
    facade_color: HexColor | None = Field(None, description="Facade color (hex)")
    roof_color: HexColor | None = Field(None, description="Roof color (hex)")

    # Geometry
    geometry: Annotated[Geometry, GeometryTypeConstraint("Polygon", "MultiPolygon")] = (
        Field(..., description="Geometry (Polygon or MultiPolygon)")
    )


# Register Pydantic models when module is imported
register_model("buildings", "building_part", BuildingPart)
