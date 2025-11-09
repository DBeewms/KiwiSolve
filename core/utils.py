"""utils.py — Utilidades compartidas de estructuras.

Propósito
---------
Reunir pequeñas funciones reutilizables usadas por varios módulos del core,
para evitar duplicación y mantener una semántica uniforme.

Funciones
---------
- es_secuencia(obj): True si obj es list o tuple (y no es str).
- es_matriz(M): True si M es lista/tupla de filas, y cada fila es lista/tupla.
- normalizar_a_matriz(M):
  - Si M es 2D (lista de filas que son listas/tuplas) -> lista de listas.
  - Si M es 1D (lista/tupla) -> matriz 1xN.
  - Si M es escalar -> [[M]].

Nota: Esta normalización no aplica el "modo numérico" (ver number_mode);
solo reestructura la forma.
"""

from typing import Any, List


def es_secuencia(obj: Any) -> bool:
    """True si es list o tuple (excluye cadenas)."""
    if isinstance(obj, str):
        return False
    return isinstance(obj, (list, tuple))

def es_matriz(M: Any) -> bool:
    """True si M es matriz 2D (lista/tupla de filas que son listas/tuplas)."""
    if not isinstance(M, (list, tuple)):
        return False
    return all(isinstance(fila, (list, tuple)) for fila in M)


def normalizar_a_matriz(M: Any) -> List[list]:
    """Convierte escalar/1D/2D a una matriz (lista de listas) sin alterar valores."""
    # 2D
    if es_secuencia(M) and any(es_secuencia(r) for r in M):
        return [list(r) for r in M]  # type: ignore[list-item]
    # 1D -> 1xN
    if es_secuencia(M):
        return [list(M)]  # type: ignore[list-item]
    # escalar -> 1x1
    return [[M]]


__all__ = [
    "es_secuencia",
    "es_matriz",
    "normalizar_a_matriz",
]
