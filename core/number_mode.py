"""
number_mode.py — Política de números unificada para KiwiSolve.

Propósito
- Unificar cómo representamos y comparamos números en todo el proyecto.
- Dos modos: exacto con Fraction (por defecto) o aproximado con float.

Resumen de la API pública (en español):
- configurar_modo_numerico(modo, decimales=6, tolerancia=1e-9)
- convertir_a_numero(x)
- convertir_a_matriz(M)
- son_iguales(a, b), es_cero(x), es_uno(x)

Compatibilidad: toda la API se expone exclusivamente en español.

Notas
- Este módulo no depende de Django, se puede testear en aislamiento.
"""

from fractions import Fraction
from decimal import Decimal
from .utils import es_secuencia as _es_secuencia

# --- Estado global mínimo -----------------------------------------------------
# "fraction" (exacto) o "float" (aproximado)
_modo = "fraction"
# sólo se usa cuando _modo == "float"
_decimales = 6
_tolerancia = 1e-9

# --- Utilidades internas ------------------------------------------------------

 # es_secuencia ahora se importa desde core.utils para evitar duplicación.


def _redondear_float(x):
    """Redondea a "_decimales" decimales y devuelve float."""
    return round(float(x), _decimales)


def _parsear_cadena_fraccion(s):
    """Convierte una cadena a Fraction.

    Soporta:
    - "a/b" -> Fraction(a, b)
    - "3.14", "1e-3", "2" -> Fraction(s) (parseo exacto desde cadena)
    """
    try:
        texto = str(s).strip()
        if "/" in texto:
            num, den = texto.split("/", 1)
            return Fraction(int(num.strip()), int(den.strip()))
        # Fraction(str_decimal) parsea de forma exacta números decimales escritos como texto
        return Fraction(texto)
    except Exception as e:  # noqa: BLE001
        raise TypeError(f"cadena '{s}' no convertible a Fraction") from e


def _parsear_cadena_float(s):
    """Convierte una cadena a float respetando fracciones "a/b" y redondea.

    Soporta:
    - "a/b" -> a/b como float
    - "3.14", "1e-3", "2" -> float(s)
    """
    try:
        texto = str(s).strip()
        if "/" in texto:
            num, den = texto.split("/", 1)
            valor = float(int(num.strip()) / int(den.strip()))
            return _redondear_float(valor)
        return _redondear_float(float(texto))
    except Exception as e:  # noqa: BLE001
        raise TypeError(f"cadena '{s}' no convertible a float") from e


def _a_fraccion_escalar(x):
    """Convierte un escalar soportado a Fraction.

    Admite int, float, Decimal, Fraction y str (incluye "a/b").
    """
    if isinstance(x, Fraction):
        return x
    if isinstance(x, bool) or x is None:
        raise TypeError("escalar inválido para conversión a Fraction")
    if isinstance(x, int):
        return Fraction(x)
    if isinstance(x, float):
        # Evitar errores binarios: convertir desde representación decimal
        return Fraction(str(x))
    if isinstance(x, Decimal):
        return Fraction(str(x))
    if isinstance(x, str):
        return _parsear_cadena_fraccion(x)
    raise TypeError(f"tipo {type(x).__name__} no convertible a Fraction")


def _a_float_escalar(x):
    """Convierte un escalar soportado a float redondeado a "_decimales".

    Admite int, float, Decimal, Fraction y str (incluye "a/b").
    """
    if isinstance(x, bool) or x is None:
        raise TypeError("escalar inválido para conversión a float")
    if isinstance(x, Fraction):
        return _redondear_float(float(x))
    if isinstance(x, int):
        return _redondear_float(float(x))
    if isinstance(x, float):
        return _redondear_float(x)
    if isinstance(x, Decimal):
        return _redondear_float(float(x))
    if isinstance(x, str):
        return _parsear_cadena_float(x)
    raise TypeError(f"tipo {type(x).__name__} no convertible a float")

# --- API pública --------------------------------------------------------------

def configurar_modo_numerico(modo, decimales=6, tolerancia=1e-9):
    """Configura el modo numérico global.

    Parámetros
    - modo: "fraction" (exacto) o "float" (aproximado).
    - decimales: redondeo cuando el modo es "float" (round(x, decimales)).
    - tolerancia: tolerancia para comparaciones en modo "float".

    Errores
    - ValueError si el modo es inválido o si decimales/tolerancia son negativos.
    """
    global _modo, _decimales, _tolerancia

    if modo not in ("fraction", "float"):
        raise ValueError("modo debe ser 'fraction' o 'float'")
    if decimales < 0:
        raise ValueError("decimales debe ser >= 0")
    if tolerancia < 0:
        raise ValueError("tolerancia debe ser >= 0")

    _modo = modo
    _decimales = int(decimales)
    _tolerancia = float(tolerancia)


def convertir_a_numero(x):
    """Convierte a número según el modo activo.

    Acepta:
    - Escalares: int, float, Fraction, Decimal, str ("a/b", "3.14", "2").
    - Secuencias (list/tuple): aplica conversión elemento a elemento (vector 1D).

    Para normalizar matrices 2D usa "convertir_a_matriz".

    Devuelve:
        Escalar del tipo del modo (Fraction o float) o una lista 1D de ellos.
    """
    if _es_secuencia(x):
        return [convertir_a_numero(v) for v in x]  # vector 1D

    if _modo == "float":
        return _a_float_escalar(x)
    return _a_fraccion_escalar(x)


def convertir_a_matriz(M):
    """Normaliza la entrada a una matriz (lista de listas) del modo activo.

    Casos soportados:
    - 2D: lista/tupla de filas -> [[...], [...]]
    - 1D: lista/tupla -> [[...vector...]] (1xN)
    - Escalar -> [[valor]] (1x1)
    """
    # 2D
    if _es_secuencia(M) and any(_es_secuencia(r) for r in M):
        return [[convertir_a_numero(v) for v in r] for r in M]  # type: ignore[index]
    # 1D vector -> 1xN
    if _es_secuencia(M):
        return [[convertir_a_numero(v) for v in M]]
    # escalar -> 1x1
    return [[convertir_a_numero(M)]]


def son_iguales(a, b):
    """Compara igualdad de escalares respetando el modo activo.

    - Modo "fraction": igualdad exacta.
    - Modo "float": se considera igual si |a - b| <= tolerancia tras convertir y redondear.
    """
    if _modo == "fraction":
        return _a_fraccion_escalar(a) == _a_fraccion_escalar(b)
    af = _a_float_escalar(a)
    bf = _a_float_escalar(b)
    return abs(af - bf) <= _tolerancia


def es_cero(x):
    """Devuelve True si x es cero bajo el modo activo."""
    return son_iguales(x, 0)


def es_uno(x):
    """Devuelve True si x es uno bajo el modo activo."""
    return son_iguales(x, 1)

# No se definen alias en inglés: preferimos una API coherente en español.
