"""Overture Maps schema validation package."""

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

try:
    import importlib.metadata

    __version__ = importlib.metadata.version("overture-schema-validation")
except ImportError:
    __version__ = "unknown"
