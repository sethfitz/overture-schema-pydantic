"""Overture Maps schema validation package."""

try:
    import importlib.metadata

    __version__ = importlib.metadata.version("overture-schema-validation")
except ImportError:
    __version__ = "unknown"
