"""
Attempt to create a friendly API for doing geometry, using 3D PGA
(projective geometric algebra) under the hood.
"""


__version__ = "0.0.1"
version_info = tuple(map(int, __version__.split(".")))


from ._geo import Point, Line, Plane  # noqa
from ._geo import Transform, Rotor, Translator  # noqa
