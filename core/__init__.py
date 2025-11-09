"""Core utilities package.

Currently exposes number_mode configuration utilities for unified numeric behavior
across algebra operations.
"""

from .number_mode import (
    configurar_modo_numerico,
    convertir_a_numero,
    convertir_a_matriz,
    es_cero,
    es_uno,
    son_iguales,
)
from .parse import (
    parsear_escalar,
    parsear_vector,
    parsear_matriz,
)
from .format import (
     formatear_escalar,
     formatear_matriz,
)
from .validate import (
    asegurar_rectangular,
    asegurar_cuadrada,
    asegurar_multiplicable,
    asegurar_aumentada,
    asegurar_intervalo,
    asegurar_cambio_signo,
)
from .steps import (
    Steps,
)
from .matrix_utils import (
    ceros,
    identidad,
    copiar,
    aumentar,
    dividir_aumentada,
    intercambiar_filas,
    escalar_fila,
    sumar_multiplo_fila,
    buscar_fila_pivote,
)

__all__ = [
    "configurar_modo_numerico",
    "convertir_a_numero",
    "convertir_a_matriz",
    "es_cero",
    "es_uno",
    "son_iguales",
    "parsear_escalar",
    "parsear_vector",
    "parsear_matriz",
     "formatear_escalar",
     "formatear_matriz",
    "asegurar_rectangular",
    "asegurar_cuadrada",
    "asegurar_multiplicable",
    "asegurar_aumentada",
    "asegurar_intervalo",
    "asegurar_cambio_signo",
    "Steps",
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
