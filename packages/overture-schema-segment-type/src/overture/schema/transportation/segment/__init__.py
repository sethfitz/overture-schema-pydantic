"""Segment type models for Overture Maps."""

# Register theme-type mappings for strict validation
from overture.schema.core.base import add_theme_type_mapping

from .models import SegmentFeature, SegmentProperties

add_theme_type_mapping("transportation", "segment")

# Register validation rules for transportation segments
from overture.schema.core.validation_rules import (
    VALID_ROAD_FLAGS,
    VALID_TRAVEL_MODES,
    DataTypeRule,
    DiscriminatedUnionRule,
    EnumValidationRule,
    ExtensibleObjectRule,
    NamesValidationRule,
    RequiredPropertyRule,
    RoadFlagsStructureRule,
    UniqueArrayRule,
    register_validation_rules,
)

# Common segment properties that apply to all subtypes
base_segment_rules = [
    RequiredPropertyRule("properties.theme", "theme property is required"),
    RequiredPropertyRule("properties.type", "type property is required"),
    RequiredPropertyRule("properties.version", "version property is required"),
    RequiredPropertyRule("properties.subtype", "subtype property is required"),
    EnumValidationRule("properties.theme", {"transportation"}, "Invalid theme value"),
    EnumValidationRule("properties.type", {"segment"}, "Invalid type value"),
    NamesValidationRule("properties.names", "Invalid names structure"),
]

# Road-specific validation rules
road_specific_rules = [
    EnumValidationRule(
        "properties.class",
        {
            "motorway",
            "primary",
            "secondary",
            "tertiary",
            "residential",
            "living_street",
            "trunk",
            "unclassified",
            "service",
            "pedestrian",
            "footway",
            "steps",
            "path",
            "track",
            "cycleway",
            "bridleway",
            "unknown",
        },
        "Invalid road class",
    ),
    RoadFlagsStructureRule("properties.road_flags", "Invalid road_flags structure"),
    EnumValidationRule(
        "properties.road_flags", VALID_ROAD_FLAGS, "Invalid road flag value"
    ),
    UniqueArrayRule("properties.road_flags", "Duplicate road flags not allowed"),
    DataTypeRule("properties.road_flags", list, "road_flags must be an array"),
]

# Rail-specific validation rules
rail_specific_rules = [
    EnumValidationRule(
        "properties.class",
        {
            "funicular",
            "light_rail",
            "monorail",
            "narrow_gauge",
            "standard_gauge",
            "subway",
            "tram",
            "unknown",
        },
        "Invalid rail class",
    ),
    EnumValidationRule(
        "properties.rail_flags",
        {
            "is_bridge",
            "is_tunnel",
            "is_under_construction",
            "is_abandoned",
            "is_covered",
            "is_passenger",
            "is_freight",
            "is_disused",
        },
        "Invalid rail flag value",
    ),
    UniqueArrayRule("properties.rail_flags", "Duplicate rail flags not allowed"),
]

# Water-specific validation rules
water_specific_rules = [
    # Water segments have minimal specific validation
]

# Create discriminated union for segment subtypes
segment_discriminated_union = DiscriminatedUnionRule(
    "properties.subtype",
    {
        "road": base_segment_rules + road_specific_rules,
        "rail": base_segment_rules + rail_specific_rules,
        "water": base_segment_rules + water_specific_rules,
    },
    "Invalid segment subtype or subtype-specific validation failed",
)

# Properties that should be extensible (allow ext_ prefixed properties)
extensible_properties = ExtensibleObjectRule(
    "properties",
    {
        "theme",
        "type",
        "subtype",
        "version",
        "class",
        "names",
        "connectors",
        "routes",
        "destinations",
        "level",
        "level_rules",
        "subclass_rules",
        "access_restrictions",
        "road_surface",
        "road_flags",
        "speed_limits",
        "width_rules",
        "prohibited_transitions",
        "subclass",
        "rail_flags",
        "sources",
    },
    "ext_",
    "Unrecognized properties must use 'ext_' prefix",
)

# Register all segment rules
segment_rules = [
    segment_discriminated_union,
    extensible_properties,
]

register_validation_rules("transportation", "segment", segment_rules)

__all__ = ["SegmentFeature", "SegmentProperties"]
