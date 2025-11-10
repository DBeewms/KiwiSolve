"""Servicios de álgebra — operaciones sobre matrices usando el núcleo.

Todas las funciones exponen una API en español y usan los módulos del
núcleo (`core`) para parseo, validación, modo numérico y formateo.

Contrato básico (por función):
- Entradas: texto con matrices estilo [[...],[...]], y opcionalmente Steps.
- Salida: dict con claves:
    - ok: bool
    - datos: payload con resultados crudos y formateados
    - error: mensaje en español si falla
    - pasos: historial Steps si se pasó un registrador
"""

from typing import Any, Dict, List, Optional

from core.parse import parsear_matriz
from core.number_mode import (
    convertir_a_matriz,
)
from core.validate import (
    asegurar_rectangular,
    asegurar_cuadrada,
    asegurar_multiplicable,
)
from core.format import formatear_matriz, formatear_escalar
from core.number_mode import es_cero
from core.steps import Steps


def _copiar_matriz(M: List[List[Any]]):
    return [list(f) for f in M]


def _matmul(A: List[List[Any]], B: List[List[Any]]):
    """Producto matricial simple (sin numpy) compatible con Fraction/float."""
    asegurar_multiplicable(A, B)
    m, n = len(A), len(A[0])
    p = len(B[0])
    C = [[0 for _ in range(p)] for _ in range(m)]
    for i in range(m):
        for j in range(p):
            s = 0
            for k in range(n):
                s = s + A[i][k] * B[k][j]
            C[i][j] = s
    return C


def _determinante_por_gauss(M: List[List[Any]], steps: Optional[Steps] = None):
    """Determinante por eliminación gaussiana con pivoteo parcial simple.

    - Solo usa operaciones de fila de resta de múltiplos (no escalado),
      por lo que el determinante es el producto de la diagonal de la forma
      triangular superior, multiplicado por (-1)^n_swaps.
    - Usa `es_cero` del modo numérico para detectar pivotes nulos.
    """
    asegurar_cuadrada(M)
    n = len(M)
    A = _copiar_matriz(M)
    swaps = 0
    if steps:
        steps.add("comienza eliminación", {"n": n})
    for i in range(n):
        # Buscar pivote en columna i a partir de fila i
        piv = i
        while piv < n and es_cero(A[piv][i]):
            piv += 1
        if piv == n:
            if steps:
                steps.add("columna sin pivote no nulo", {"col": i})
            return 0
        if piv != i:
            A[i], A[piv] = A[piv], A[i]
            swaps += 1
            if steps:
                steps.add("intercambiar filas", {"i": i, "piv": piv})
        # Eliminar entradas por debajo del pivote
        piv_val = A[i][i]
        for j in range(i + 1, n):
            if es_cero(A[j][i]):
                continue
            factor = A[j][i] / piv_val
            for k in range(i, n):
                A[j][k] = A[j][k] - factor * A[i][k]
            if steps:
                steps.add("restar múltiplo de fila", {"fila": j, "de": i, "factor": str(factor)})
    # Producto de la diagonal
    det = 1
    for i in range(n):
        det = det * A[i][i]
    if swaps % 2 == 1:
        det = -det
    if steps:
        steps.add("producto de diagonal", {"swaps": swaps, "diag": [str(A[i][i]) for i in range(n)]})
    return det


def multiplicar_matrices(texto_A: str, texto_B: str, steps: Optional[Steps] = None) -> Dict[str, Any]:
    if steps:
        steps.begin("multiplicacion_matrices")
    try:
        A_raw = parsear_matriz(texto_A)
        B_raw = parsear_matriz(texto_B)
        if steps:
            steps.add("parsear entradas")
        A = convertir_a_matriz(A_raw)
        B = convertir_a_matriz(B_raw)
        asegurar_rectangular(A)
        asegurar_rectangular(B)
        asegurar_multiplicable(A, B)
        if steps:
            steps.add("validar dimensiones", {"A": [len(A), len(A[0])], "B": [len(B), len(B[0])]})
        C = _matmul(A, B)
        if steps:
            steps.add("producto realizado")
        datos = {
            "A": A,
            "B": B,
            "C": C,
            "C_formateada": formatear_matriz(C, modo="auto"),
        }
        if steps:
            steps.end({"ok": True})
        return {"ok": True, "datos": datos, "error": None, "pasos": steps.to_list() if steps else []}
    except Exception as e:  # noqa: BLE001
        if steps:
            steps.add("error", {"mensaje": str(e)})
            steps.end({"ok": False})
        return {"ok": False, "datos": {}, "error": str(e), "pasos": steps.to_list() if steps else []}


def determinante(texto_M: str, steps: Optional[Steps] = None) -> Dict[str, Any]:
    if steps:
        steps.begin("determinante")
    try:
        M_raw = parsear_matriz(texto_M)
        if steps:
            steps.add("parsear entrada")
        M = convertir_a_matriz(M_raw)
        asegurar_cuadrada(M)
        if steps:
            steps.add("validar cuadrada", {"n": len(M)})
        det = _determinante_por_gauss(M, steps=steps)
        datos = {
            "M": M,
            "det": det,
            "det_formateado": formatear_escalar(det, modo="auto"),
        }
        if steps:
            steps.end({"ok": True})
        return {"ok": True, "datos": datos, "error": None, "pasos": steps.to_list() if steps else []}
    except Exception as e:  # noqa: BLE001
        if steps:
            steps.add("error", {"mensaje": str(e)})
            steps.end({"ok": False})
        return {"ok": False, "datos": {}, "error": str(e), "pasos": steps.to_list() if steps else []}


__all__ = [
    "multiplicar_matrices",
    "determinante",
    "sumar_matrices",
]


def sumar_matrices(texto_A: str, texto_B: str, modo_formato: str = "fraction") -> Dict[str, Any]:
    """Suma de matrices A + B.

    Parámetros:
      - texto_A, texto_B: cadenas estilo [[...],[...]]
      - modo_formato: "fraction" | "float" | "auto" para la salida

    Reglas:
      - Ambas deben ser rectangulares y de mismas dimensiones.
    """
    try:
        A_raw = parsear_matriz(texto_A)
        B_raw = parsear_matriz(texto_B)
        A = convertir_a_matriz(A_raw)
        B = convertir_a_matriz(B_raw)
        asegurar_rectangular(A)
        asegurar_rectangular(B)
        if len(A) == 0 or len(B) == 0:
            raise ValueError("Matrices vacías no se pueden sumar")
        if len(A) != len(B) or len(A[0]) != len(B[0]):
            raise ValueError("Dimensiones incompatibles para suma (A y B deben coincidir)")
        filas, cols = len(A), len(A[0])
        C = [[A[i][j] + B[i][j] for j in range(cols)] for i in range(filas)]
        datos = {
            "A": A,
            "B": B,
            "C": C,
            "C_formateada": formatear_matriz(C, modo=modo_formato),
        }
        return {"ok": True, "datos": datos, "error": None, "pasos": []}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "datos": {}, "error": str(e), "pasos": []}
