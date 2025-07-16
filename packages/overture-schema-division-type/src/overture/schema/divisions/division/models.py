"""Division models for Overture Maps divisions theme."""

from typing import Annotated, Dict, List, Optional

from pydantic import Field

from overture.schema.core.base import (
    CartographyContainer,
    OvertureFeature,
    register_model,
)
from overture.schema.core.common import (
    NamesContainer,
)
from overture.schema.core.geometry import Geometry, GeometryTypeConstraint
from overture.schema.divisions.common import (
    CapitalOfDivisionItem,
    DivisionClass,
    HierarchyItem,
    Norms,
    Perspectives,
    PlaceType,
    parent_division_required_unless,
)
from overture.schema.validation import (
    ConstraintValidatedModel,
    CountryCode,
    MinItemsConstraint,
    NoWhitespaceString,
    RegionCode,
    UniqueItemsConstraint,
    theme_literal,
    type_literal,
)


@parent_division_required_unless("subtype", PlaceType.COUNTRY)
class Division(OvertureFeature, ConstraintValidatedModel):
    """Division feature model."""

    # Override theme and type with constraint-based validation
    theme: theme_literal("divisions") = Field("divisions", description="Feature theme")
    type: type_literal("division") = Field("division", description="Feature type")

    # Required properties
    subtype: PlaceType = Field(..., description="Administrative level")

    # Administrative hierarchy - each hierarchy must have unique items and at least one item
    hierarchies: Annotated[
        List[
            Annotated[
                List[HierarchyItem], MinItemsConstraint(1), UniqueItemsConstraint()
            ]
        ],
        MinItemsConstraint(1),
    ] = Field(..., description="Administrative hierarchy chains")

    # Geographic context
    country: CountryCode = Field(..., description="ISO 3166-1 alpha-2 country code")
    region: Optional[RegionCode] = Field(None, description="ISO 3166-2 region code")

    # Relationships
    parent_division_id: Optional[NoWhitespaceString] = Field(
        None, min_length=1, description="Parent division identifier"
    )
    capital_division_ids: Optional[
        Annotated[List[NoWhitespaceString], UniqueItemsConstraint()]
    ] = Field(None, min_length=1, description="Capital division identifiers")
    capital_of_divisions: Optional[
        Annotated[
            List[CapitalOfDivisionItem], MinItemsConstraint(1), UniqueItemsConstraint()
        ]
    ] = Field(None, description="Divisions this is capital of")

    # Political and social context
    perspectives: Optional[Perspectives] = Field(
        None, description="Political perspectives"
    )
    norms: Optional[Norms] = Field(None, description="Local norms")

    # Localization
    local_type: Optional[Dict[str, str]] = Field(
        None, description="Localized subtype name"
    )

    # Population and ranking
    population: Optional[int] = Field(None, ge=0, description="Population count")
    prominence: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Prominence score (0.0-1.0)"
    )

    # Optional classification
    class_: Optional[DivisionClass] = Field(
        None, alias="class", description="Division class designation"
    )

    # Complex containers
    names: Optional[NamesContainer] = Field(None, description="Multilingual names")
    cartography: CartographyContainer | None = Field(
        None, description="Cartographic display hints"
    )

    # Use constraint-based validation for Point geometry
    geometry: Annotated[Geometry, GeometryTypeConstraint("Point")] = Field(
        ..., description="Point geometry for division location"
    )


# Register the model
register_model("divisions", "division", Division)
