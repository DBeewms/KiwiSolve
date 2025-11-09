"""matrix_utils.py — Primitivas de matrices (SRP).

Propósito
---------
Reunir utilidades básicas y atómicas para construir y manipular matrices,
separadas por responsabilidad única. Todas las funciones usan nombres en
español y mensajes de error claros.

Convenciones generales
----------------------
- Las matrices son listas de listas (rectangulares).
- Las funciones no mutan las entradas: devuelven nuevas matrices copiadas.
- Se valida estructura con core.validate. Errores: ValueError si matriz vacía
  o si hay índices fuera de rango.
- Para búsquedas de pivotes se respeta la política numérica (es_cero).

Funciones
---------
Constructores:
- ceros(m, n)
- identidad(n)
- copiar(M)
- aumentar(A, B)
- dividir_aumentada(M, n_columnas_A)

Operaciones de fila (devuelven nueva matriz):
- intercambiar_filas(M, i, j)
- escalar_fila(M, i, c)
- sumar_multiplo_fila(M, i, j, c)   # F_i ← F_i + c * F_j

Búsquedas:
- buscar_fila_pivote(M, col, fila_inicio)
"""

from typing import Any, List
from .validate import asegurar_rectangular
from .number_mode import es_cero


# ----------------------------- Constructores -----------------------------

def ceros(m, n):
    """Crea una matriz m×n de ceros.

    Reglas: m y n deben ser enteros >= 1.
    """
    if not isinstance(m, int) or not isinstance(n, int):
        raise ValueError("m y n deben ser enteros")
    if m <= 0 or n <= 0:
        raise ValueError("m y n deben ser mayores que 0")
    return [[0 for _ in range(n)] for _ in range(m)]


def identidad(n):
    """Crea la matriz identidad n×n.

    Regla: n entero >= 1.
    """
    if not isinstance(n, int):
        raise ValueError("n debe ser entero")
    if n <= 0:
        raise ValueError("n debe ser mayor que 0")
    M = ceros(n, n)
    for i in range(n):
        M[i][i] = 1
    return M


def copiar(M):
    """Devuelve una copia profunda de la matriz M.

    Errores: ValueError si M no es rectangular o si está vacía.
    """
    asegurar_rectangular(M)
    if len(M) == 0:
        raise ValueError("La matriz no debe estar vacía")
    return [list(fila) for fila in M]


def aumentar(A, B):
    """Concatena horizontalmente A y B: [A | B].

    Reglas: A y B rectangulares, no vacías y con el mismo número de filas.
    """
    asegurar_rectangular(A)
    asegurar_rectangular(B)
    if len(A) == 0 or len(B) == 0:
        raise ValueError("Las matrices no deben estar vacías")
    if len(A) != len(B):
        raise ValueError("A y B deben tener el mismo número de filas para augment")
    C: List[List[Any]] = []
    for fila_a, fila_b in zip(A, B):
        C.append(list(fila_a) + list(fila_b))
    return C


def dividir_aumentada(M, n_columnas_A):
    """Divide una matriz aumentada M en (A, B), donde A son las primeras n_columnas_A columnas.

    Reglas: M rectangular, no vacía. 1 <= n_columnas_A < ncols(M).
    Devuelve una tupla (A, B).
    """
    asegurar_rectangular(M)
    if len(M) == 0:
        raise ValueError("La matriz no debe estar vacía")
    ncols = len(M[0])
    if not isinstance(n_columnas_A, int):
        raise ValueError("n_columnas_A debe ser entero")
    if n_columnas_A <= 0 or n_columnas_A >= ncols:
        raise ValueError("n_columnas_A debe estar en el rango 1..ncols-1")
    A: List[List[Any]] = []
    B: List[List[Any]] = []
    for fila in M:
        A.append(list(fila[:n_columnas_A]))
        B.append(list(fila[n_columnas_A:]))
    return A, B


# ------------------------- Operaciones de fila ---------------------------

def _validar_indices_fila(M, i):
    if i < 0 or i >= len(M):
        raise ValueError("Índice de fila fuera de rango")


def intercambiar_filas(M, i, j):
    """Intercambia las filas i y j, devolviendo una nueva matriz.

    Errores: ValueError si M vacía o índices fuera de rango.
    """
    asegurar_rectangular(M)
    if len(M) == 0:
        raise ValueError("La matriz no debe estar vacía")
    _validar_indices_fila(M, i)
    _validar_indices_fila(M, j)
    R = [list(fila) for fila in M]
    R[i], R[j] = R[j], R[i]
    return R


def escalar_fila(M, i, c):
    """Escala la fila i por el factor c: F_i ← c * F_i. Devuelve nueva matriz.

    Errores: ValueError si M vacía o índice fuera de rango.
    """
    asegurar_rectangular(M)
    if len(M) == 0:
        raise ValueError("La matriz no debe estar vacía")
    _validar_indices_fila(M, i)
    R = [list(fila) for fila in M]
    R[i] = [c * x for x in R[i]]
    return R


def sumar_multiplo_fila(M, i, j, c):
    """Suma a la fila i el múltiplo c de la fila j: F_i ← F_i + c * F_j.

    Devuelve nueva matriz. Errores: ValueError si M vacía o índice fuera de rango.
    """
    asegurar_rectangular(M)
    if len(M) == 0:
        raise ValueError("La matriz no debe estar vacía")
    _validar_indices_fila(M, i)
    _validar_indices_fila(M, j)
    R = [list(fila) for fila in M]
    R[i] = [xi + c * xj for xi, xj in zip(R[i], R[j])]
    return R


# ------------------------------ Búsquedas -------------------------------

def buscar_fila_pivote(M, col, fila_inicio):
    """Busca el índice de la primera fila con pivote no nulo en la columna 'col'.

    Reglas: M rectangular y no vacía; 0 <= col < ncols; 0 <= fila_inicio < nrows.
    Devuelve el índice de fila o None si no se encuentra pivote.
    """
    asegurar_rectangular(M)
    if len(M) == 0:
        raise ValueError("La matriz no debe estar vacía")
    nrows = len(M)
    ncols = len(M[0])
    if not isinstance(col, int) or not isinstance(fila_inicio, int):
        raise ValueError("col y fila_inicio deben ser enteros")
    if col < 0 or col >= ncols:
        raise ValueError("col fuera de rango")
    if fila_inicio < 0 or fila_inicio >= nrows:
        raise ValueError("fila_inicio fuera de rango")
    for k in range(fila_inicio, nrows):
        if not es_cero(M[k][col]):
            return k
    return None


__all__ = [
    "ceros",
    "identidad",
    "copiar",
    "aumentar",
    "dividir_aumentada",
    "intercambiar_filas",
    "escalar_fila",
    "sumar_multiplo_fila",
    "buscar_fila_pivote",
]
