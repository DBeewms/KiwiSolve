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

__all__ = [
    "set_number_mode",
    "to_num",
    "to_matrix",
    "is_zero",
    "is_one",
    "eq",
]
