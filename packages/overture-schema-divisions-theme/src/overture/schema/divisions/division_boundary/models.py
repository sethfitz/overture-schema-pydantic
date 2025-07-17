"""Division boundary models for Overture Maps divisions theme."""

from typing import Annotated

from pydantic import Field

from overture.schema.core.base import (
    OvertureFeature,
    register_model,
)
from overture.schema.core.geometry import Geometry, GeometryTypeConstraint
from overture.schema.validation import (
    ConstraintValidatedModel,
    CountryCode,
    RegionCode,
    UniqueItemsConstraint,
    mutually_exclusive,
    not_required_if,
    theme_literal,
    type_literal,
)

from ..shared import (
    AreaBoundaryClass,
    Perspectives,
    PlaceType,
)


@mutually_exclusive("is_land", "is_territorial")
@not_required_if("subtype", PlaceType.COUNTRY, ["country"])
class DivisionBoundary(OvertureFeature, ConstraintValidatedModel):
    """Division boundary feature model."""

    # Override theme and type with constraint-based validation
    theme: theme_literal("divisions") = Field("divisions", description="Feature theme")
    type: type_literal("division_boundary") = Field(
        "division_boundary", description="Feature type"
    )

    # Required properties
    subtype: PlaceType = Field(..., description="Administrative level")
    class_: AreaBoundaryClass = Field(
        ..., alias="class", description="Boundary class (land/maritime)"
    )
    division_ids: Annotated[list[str], UniqueItemsConstraint()] = Field(
        ..., min_length=2, max_length=2, description="Two division IDs (left/right)"
    )

    # Geographic context
    country: CountryCode | None = Field(
        None,
        description="ISO 3166-1 alpha-2 country code (not for country boundaries)",
    )
    region: RegionCode | None = Field(None, description="ISO 3166-2 region code")

    # Territorial designation (exclusive or) - strict boolean validation
    is_land: bool | None = Field(
        None, description="Land boundary designation", strict=True
    )
    is_territorial: bool | None = Field(
        None, description="Territorial boundary designation", strict=True
    )

    # Dispute status
    is_disputed: bool | None = Field(None, description="Boundary is disputed")

    # Political and social context
    perspectives: Perspectives | None = Field(
        None, description="Political perspectives"
    )

    geometry: Annotated[
        Geometry, GeometryTypeConstraint("LineString", "MultiLineString")
    ] = Field(..., description="Geometry (LineString or MultiLineString)")


# Register the model
register_model("divisions", "division_boundary", DivisionBoundary)
