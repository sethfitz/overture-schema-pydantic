"""Division area models for Overture Maps divisions theme."""

from typing import Annotated, List, Optional

from pydantic import Field

from overture.schema.core.base import (
    OvertureFeature,
    OvertureFeatureProperties,
    register_model,
)
from overture.schema.core.common import (
    AdvancedSourceItem,
    NamesContainer,
)
from overture.schema.core.geometry import Geometry, GeometryTypeConstraint
from overture.schema.divisions.common.models import (
    AreaBoundaryClass,
    PlaceType,
)
from overture.schema.validation import (
    MutuallyExclusiveConstraint,
    theme_literal,
    type_literal,
)


class DivisionAreaProperties(
    Annotated[
        OvertureFeatureProperties,
        MutuallyExclusiveConstraint("is_land", "is_territorial"),
    ]
):
    """Properties specific to division area features."""

    # Override theme and type with constraint-based validation
    theme: theme_literal("divisions") = Field("divisions", description="Feature theme")
    type: type_literal("division_area") = Field(
        "division_area", description="Feature type"
    )

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


class DivisionArea(OvertureFeature):
    """Division area feature model."""

    properties: DivisionAreaProperties = Field(
        ..., description="Division area feature properties"
    )
    geometry: Annotated[Geometry, GeometryTypeConstraint("Polygon", "MultiPolygon")] = (
        Field(..., description="Geometry (Polygon or MultiPolygon)")
    )


# Register the model
register_model("divisions", "division_area", DivisionArea)
