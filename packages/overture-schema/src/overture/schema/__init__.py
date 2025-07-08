"""
Overture Maps complete schema collection.

This package provides convenient access to all Overture Maps themes and types.
Import specific schemas from their respective theme packages:

    from overture.schema.base import Infrastructure
    from overture.schema.buildings import Building
    from overture.schema.transportation import Segment
    from overture.schema.places import Place
    from overture.schema.divisions import Division
    from overture.schema.addresses import Address
"""

__path__ = __import__("pkgutil").extend_path(__path__, __name__)
