"""validate.py — Validaciones de dimensiones y precondiciones (fail-fast).

Objetivo
--------
Proveer funciones simples para verificar rápidamente que las estructuras
numéricas cumplen con las condiciones requeridas antes de realizar
operaciones algebraicas o numéricas más costosas.

Todas las funciones lanzan ValueError con mensaje directo y claro en español
si la condición no se cumple.

Funciones principales
---------------------
- asegurar_rectangular(A): A debe ser lista de listas y todas las filas con
  la misma longitud (>0 filas opcionalmente; matriz vacía se considera válida).
- asegurar_cuadrada(A): A debe ser rectangular y nfilas == ncols.
- asegurar_multiplicable(A, B): A y B rectangulares y columnas de A == filas de B.
- asegurar_aumentada(M): verifica que la matriz tenga exactamente una columna
  adicional respecto al número de filas (forma típica de matriz aumentada en
  sistemas lineales Ax=b representada como [A|b]).
- asegurar_intervalo(a, b): verifica a < b.
- asegurar_cambio_signo(f, a, b): requiere asegurar_intervalo y f(a)*f(b) < 0.

Convenciones
------------
Se espera que A, B, M sean listas de listas numéricas (no se verifica tipo
numérico aquí, sólo estructura). Para intervalos se asume que a, b son números
comparables (int/float/Fraction, etc.).
"""

from typing import Callable, Any
from .utils import es_matriz


# Nota: La detección de matriz 2D se centraliza en utils.es_matriz para evitar duplicación.


def asegurar_rectangular(A):
    """Verifica que A sea una matriz rectangular.

    Reglas:
    - Si A es matriz vacía (len(A) == 0) se considera rectangular (caso trivial).
    - Todas las filas deben tener la misma longitud.
    """
    if not es_matriz(A):
        raise ValueError("A debe ser una matriz (lista de listas)")
    if len(A) == 0:
        return A
    longitudes = [len(f) for f in A]
    if any(l != longitudes[0] for l in longitudes):
        raise ValueError("A debe ser rectangular (todas las filas misma longitud)")
    return A


def asegurar_cuadrada(A):
    """Verifica que A sea cuadrada (nfilas == ncols)."""
    asegurar_rectangular(A)
    if len(A) == 0:
        raise ValueError("A debe tener al menos una fila para ser cuadrada")
    nfilas = len(A)
    ncols = len(A[0])
    if nfilas != ncols:
        raise ValueError("A debe ser cuadrada")
    return A


def asegurar_multiplicable(A, B):
    """Verifica que A y B puedan multiplicarse (A_cols == B_rows)."""
    asegurar_rectangular(A)
    asegurar_rectangular(B)
    if len(A) == 0 or len(B) == 0:
        raise ValueError("Matrices vacías no se pueden multiplicar")
    a_cols = len(A[0])
    b_rows = len(B)
    if a_cols != b_rows:
        raise ValueError("Dimensiones incompatibles para multiplicación (cols(A) != rows(B))")
    return A, B


def asegurar_aumentada(M):
    """Verifica que M sea una matriz aumentada típica de sistema lineal Ax=b.

    Reglas:
    - M rectangular.
    - ncols == nfilas + 1 (columna extra para términos independientes).
    """
    asegurar_rectangular(M)
    if len(M) == 0:
        raise ValueError("Matriz aumentada vacía inválida")
    nfilas = len(M)
    ncols = len(M[0])
    if ncols != nfilas + 1:
        raise ValueError("M debe ser aumentada (ncols == nfilas + 1)")
    return M


def asegurar_intervalo(a, b):
    """Verifica que a < b para definir un intervalo abierto (a, b)."""
    if a >= b:
        raise ValueError("Intervalo inválido: se requiere a < b")
    return a, b


def asegurar_cambio_signo(f: Callable[[Any], Any], a, b):
    """Verifica que f(a) y f(b) tengan signos opuestos (bisección).

    Pasos:
    - asegurar_intervalo(a, b)
    - Evalúa f(a), f(b) (se asume que f es pura y no lanza)
    - Comprueba f(a) * f(b) < 0
    """
    asegurar_intervalo(a, b)
    fa = f(a)
    fb = f(b)
    try:
        prod = fa * fb
    except Exception as e:  # noqa: BLE001
        raise ValueError("f(a) y f(b) deben ser valores numéricos multiplicables") from e
    if prod >= 0:
        raise ValueError("No hay cambio de signo en el intervalo (f(a)*f(b) >= 0)")
    return a, b, fa, fb


__all__ = [
    "asegurar_rectangular",
    "asegurar_cuadrada",
    "asegurar_multiplicable",
    "asegurar_aumentada",
    "asegurar_intervalo",
    "asegurar_cambio_signo",
]
