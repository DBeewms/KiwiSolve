"""format.py — Salida legible y consistente para escalares y matrices.

Objetivo
--------
Ofrecer funciones de formateo sencillas y explícitas:

- formatear_escalar(x, modo="auto", decimales=6)
    Devuelve una cadena con una representación humana de x.
    Modos:
      - "auto": si se puede escribir como decimal finito, se muestra como
        decimal recortado (sin ceros sobrantes); en caso contrario, se usa
        fracción "a/b".
      - "fraction": siempre en forma fracción (salvo enteros, que van como
        número entero sin "/1").
            - "float": siempre como decimal, con un máximo de "decimales" dígitos.

- formatear_matriz(M, modo="auto", decimales=6)
        Devuelve una matriz de cadenas list[list[str]], aplicando formatear_escalar a cada
    elemento. Acepta escalar, vector 1D o matriz 2D y normaliza a 2D.

Notas de implementación
-----------------------
- Decimal finito: una fracción p/q (en términos reducidos) tiene decimal finito
  si y solo si q tiene como factores primos sólo 2 y 5. En ese caso generamos
  el decimal exacto y recortamos ceros a la derecha. Si el número de decimales
    exactos excede "decimales", redondeamos a ese límite para mantener legibilidad.
"""

from fractions import Fraction
from decimal import Decimal, getcontext, ROUND_HALF_UP
from .utils import es_secuencia, normalizar_a_matriz


# -------------------- utilidades internas de estructura ---------------------

 # es_secuencia y normalizar_a_matriz ahora se importan desde core.utils para evitar duplicación.


# -------------------- utilidades internas de números ------------------------

def _a_fraction_exacto(x):
    """Convierte a Fraction preservando la intención humana para float/Decimal.

    - int -> Fraction(int)
    - Fraction -> tal cual
    - float/Decimal -> Fraction(str(x)) para evitar artefactos binarios
    - str -> no soportado aquí (el caller debe parsear antes)
    """
    if isinstance(x, Fraction):
        return x
    if isinstance(x, int):
        return Fraction(x, 1)
    if isinstance(x, float):
        return Fraction(str(x))
    if isinstance(x, Decimal):
        return Fraction(str(x))
    raise TypeError("tipo no soportado para conversión a Fraction en formato")


def _factor_2_5(q):
    """Devuelve (resto, a, b) tal que q = resto * 2^a * 5^b, con resto sin factores 2 ni 5."""
    a = 0
    b = 0
    while q % 2 == 0:
        q //= 2
        a += 1
    while q % 5 == 0:
        q //= 5
        b += 1
    return q, a, b


def _tiene_decimal_finito(frac):
    frac = Fraction(frac.numerator, frac.denominator)  # aseguramos reducido
    resto, _, _ = _factor_2_5(frac.denominator)
    return resto == 1


def _decimal_exacto_de_fraction(frac):
    """Construye el decimal exacto de una fracción con denominador 2^a*5^b.

    Devuelve par (texto_decimal, decimales_exactos).
    """
    f = Fraction(frac.numerator, frac.denominator)  # reducido
    signo = '-' if f < 0 else ''
    f = abs(f)
    q = f.denominator
    resto, a, b = _factor_2_5(q)
    assert resto == 1, "la fracción no tiene decimal finito"
    k = max(a, b)  # número de decimales exactos
    # Escalar numerador para llevar denominador a 10^k
    if a >= b:
        factor = 5 ** (a - b)
    else:
        factor = 2 ** (b - a)
    num10 = f.numerator * factor
    den10 = 10 ** k
    entero = num10 // den10
    resto_num = num10 % den10
    if k == 0:
        return f"{signo}{entero}", 0
    frac_str = str(resto_num).rjust(k, '0')
    # recortar ceros sobrantes
    frac_str = frac_str.rstrip('0')
    if frac_str == '':
        return f"{signo}{entero}", 0
    return f"{signo}{entero}.{frac_str}", len(frac_str)


def _redondear_decimal_str(s, decimales):
    """Redondea una cadena decimal a 'decimales' decimales y recorta ceros.

    Usa Decimal para evitar problemas de redondeo binario.
    """
    if decimales is None:
        decimales = 6
    d = Decimal(s)
    exp = Decimal('1').scaleb(-int(decimales))  # 10^-decimales
    d2 = d.quantize(exp, rounding=ROUND_HALF_UP)
    # Normalizar y recortar ceros y punto final
    s2 = format(d2, 'f')
    if '.' in s2:
        s2 = s2.rstrip('0').rstrip('.')
    return s2


def _formatear_decimal_finito(frac, decimales):
    texto, k = _decimal_exacto_de_fraction(frac)
    if k > decimales:
        return _redondear_decimal_str(texto, decimales)
    return texto


def _formatear_como_fraccion(frac):
    frac = Fraction(frac.numerator, frac.denominator)
    if frac.denominator == 1:
        return str(frac.numerator)
    return f"{frac.numerator}/{frac.denominator}"


def _formatear_como_decimal(x, decimales):
    # Caso entero
    if isinstance(x, int):
        return str(x)
    # Caso fracción: usar decimal exacto si es finito; si no, dividir con decimal
    if isinstance(x, Fraction):
        if _tiene_decimal_finito(x):
            return _formatear_decimal_finito(x, decimales)
        # No finito: usar división con Decimal y redondeo
        getcontext().prec = max(28, decimales + 5)
        d = Decimal(x.numerator) / Decimal(x.denominator)
        return _redondear_decimal_str(str(d), decimales)
    # Caso float o Decimal: convertir a Decimal por cadena, redondear y recortar
    if isinstance(x, float):
        return _redondear_decimal_str(str(x), decimales)
    if isinstance(x, Decimal):
        return _redondear_decimal_str(str(x), decimales)
    # Último recurso: intentar a Fraction y formatear
    try:
        f = _a_fraction_exacto(x)
        return _formatear_como_decimal(f, decimales)
    except Exception:  # noqa: BLE001
        raise TypeError("tipo no soportado para formateo decimal")


# -------------------- API pública -------------------------------------------

def formatear_escalar(x, modo="auto", decimales=6):
    """Formatea un escalar a cadena legible.

    Parámetros:
      - x: int, float, Fraction o Decimal.
      - modo: "auto" | "fraction" | "float".
      - decimales: máxima cantidad de decimales al mostrar como decimal.
    """
    if modo not in ("auto", "fraction", "float"):
        raise ValueError("modo debe ser 'auto', 'fraction' o 'float'")

    # Normalizamos a tipos esperados cuando conviene
    if modo == "fraction":
        # Siempre fracción (enteros sin /1)
        if isinstance(x, int):
            return str(x)
        f = _a_fraction_exacto(x)
        return _formatear_como_fraccion(f)

    if modo == "float":
        # Siempre decimal con máximo 'decimales'
        return _formatear_como_decimal(x, decimales)

    # modo == "auto"
    # Decidir por finitud decimal
    if isinstance(x, int):
        return str(x)
    if isinstance(x, Fraction):
        if _tiene_decimal_finito(x):
            return _formatear_decimal_finito(x, decimales)
        return _formatear_como_fraccion(x)
    if isinstance(x, (float, Decimal)):
        return _formatear_como_decimal(x, decimales)

    # Intentar convertir a Fraction si es un tipo compatible (p.ej. bool queda fuera)
    try:
        f = _a_fraction_exacto(x)
        if _tiene_decimal_finito(f):
            return _formatear_decimal_finito(f, decimales)
        return _formatear_como_fraccion(f)
    except Exception:  # noqa: BLE001
        raise TypeError("tipo no soportado para formato automático")


def formatear_matriz(M, modo="auto", decimales=6):
    """Formatea un escalar, vector o matriz a una matriz de cadenas.

    Devuelve list[list[str]].
    """
    matriz = normalizar_a_matriz(M)
    out = []
    for fila in matriz:
        out.append([formatear_escalar(x, modo=modo, decimales=decimales) for x in fila])
    return out


__all__ = [
    "formatear_escalar",
    "formatear_matriz",
]
