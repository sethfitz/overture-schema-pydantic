"""Division boundary models for Overture Maps divisions theme."""

from typing import Annotated, List, Optional

from pydantic import Field

from overture.schema.core.base import (
    OvertureFeature,
    OvertureFeatureProperties,
    register_model,
)
from overture.schema.core.common import (
    AdvancedSourceItem,
)
from overture.schema.core.geometry import Geometry, GeometryTypeConstraint
from overture.schema.divisions.common.models import (
    AreaBoundaryClass,
    Perspectives,
    PlaceType,
)
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


@mutually_exclusive("is_land", "is_territorial")
@not_required_if("subtype", PlaceType.COUNTRY, ["country"])
class DivisionBoundaryProperties(OvertureFeatureProperties, ConstraintValidatedModel):
    """Properties specific to division boundary features."""

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
    division_ids: Annotated[List[str], UniqueItemsConstraint()] = Field(
        ..., min_length=2, max_length=2, description="Two division IDs (left/right)"
    )

    # Geographic context
    country: Optional[CountryCode] = Field(
        None,
        description="ISO 3166-1 alpha-2 country code (not for country boundaries)",
    )
    region: Optional[RegionCode] = Field(None, description="ISO 3166-2 region code")

    # Territorial designation (exclusive or) - strict boolean validation
    is_land: Optional[bool] = Field(
        None, description="Land boundary designation", strict=True
    )
    is_territorial: Optional[bool] = Field(
        None, description="Territorial boundary designation", strict=True
    )

    # Dispute status
    is_disputed: Optional[bool] = Field(None, description="Boundary is disputed")

    # Political and social context
    perspectives: Optional[Perspectives] = Field(
        None, description="Political perspectives"
    )

    # Complex containers
    sources: Optional[List[AdvancedSourceItem]] = Field(
        None, min_length=1, description="Advanced source information"
    )


class DivisionBoundary(OvertureFeature):
    """Division boundary feature model."""

    properties: DivisionBoundaryProperties = Field(
        ..., description="Division boundary feature properties"
    )
    geometry: Annotated[
        Geometry, GeometryTypeConstraint("LineString", "MultiLineString")
    ] = Field(..., description="Geometry (LineString or MultiLineString)")


# Register the model
register_model("divisions", "division_boundary", DivisionBoundary)
