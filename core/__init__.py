"""Core utilities package.

Currently exposes number_mode configuration utilities for unified numeric behavior
across algebra operations.
"""

from .number_mode import (
    set_number_mode,
    to_num,
    to_matrix,
    is_zero,
    is_one,
    eq,
)
from .parse import (
    parse_scalar,
    parse_vector,
    parse_matrix,
)

__all__ = [
    "set_number_mode",
    "to_num",
    "to_matrix",
    "is_zero",
    "is_one",
    "eq",
    "parse_scalar",
    "parse_vector",
    "parse_matrix",
]
