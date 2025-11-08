"""parse.py — Conversión segura de texto a estructuras numéricas internas.

Propósito
---------
Convertir texto a números, vectores y matrices usando reglas restringidas y
mensajes de error claros en español, sin ejecutar código arbitrario.

Funciones públicas (resumen)
----------------------------
- parse_scalar(text)
    Convierte un escalar en una cantidad numérica (int, float o Fraction).
    Admite: enteros, decimales, fracciones a/b, paréntesis, raíz cuadrada
    (sqrt(expr)), potencia con ^ y combinaciones anidadas (p. ej. (1/2)^(3/2),
    (1/2)/(3/4), fracciones como exponentes, etc.). No se soporta suma/resta
    binaria; el signo negativo unario sí está permitido.

- parse_vector(text)
    Convierte un texto estilo [ item, item, ... ] a lista de números (usa
    parse_scalar por elemento).

- parse_matrix(text)
    Convierte un texto estilo [[fila1],[fila2],...] a lista de filas numéricas.
    Verifica que todas las filas tengan la misma longitud.

Errores
-------
Se lanza ValueError para: texto vacío; caracteres no permitidos; paréntesis
no balanceados; uso incorrecto de corchetes; denominador 0; expresión inválida.

Nota: Esta capa NO aplica el modo numérico de `number_mode`; devuelve tipos
nativos (int, float, Fraction). Si necesitas forzar el tipo del modo global,
convierte luego con `core.number_mode.convertir_a_numero`.
"""

from __future__ import annotations

from fractions import Fraction
import math


# --- Pequeñas utilidades de texto -------------------------------------------

def _limpiar(texto):
    return texto.strip()


# --- Tokenizador (sólo símbolos permitidos) ----------------------------------

class _Token:
    def __init__(self, tipo, valor=None):
        self.tipo = tipo  # 'NUM', 'SQRT', 'LPAREN', 'RPAREN', 'DIV', 'POW', 'MINUS', 'EOF'
        self.valor = valor


def _tokenizar(texto):
    """Convierte la cadena en una lista de tokens permitidos.

    Caracteres soportados: dígitos, punto decimal, '-', '/', '^', '(', ')',
    la palabra 'sqrt'. Cualquier otro carácter produce ValueError.
    """
    s = texto
    i = 0
    tokens = []
    while i < len(s):
        ch = s[i]
        if ch.isspace():
            i += 1
            continue
        if ch.isdigit():
            j = i + 1
            punto = False
            while j < len(s) and (s[j].isdigit() or (s[j] == '.' and not punto)):
                if s[j] == '.':
                    punto = True
                j += 1
            tokens.append(_Token('NUM', s[i:j]))
            i = j
            continue
        if ch == '-':
            tokens.append(_Token('MINUS'))
            i += 1
            continue
        if ch == '/':
            tokens.append(_Token('DIV'))
            i += 1
            continue
        if ch == '^':
            tokens.append(_Token('POW'))
            i += 1
            continue
        if ch == '(':
            tokens.append(_Token('LPAREN'))
            i += 1
            continue
        if ch == ')':
            tokens.append(_Token('RPAREN'))
            i += 1
            continue
        if s.startswith('sqrt', i):
            tokens.append(_Token('SQRT'))
            i += 4
            continue
        raise ValueError(f"carácter no permitido: '{ch}'")
    tokens.append(_Token('EOF'))
    return tokens


# --- Parser recursivo (gramática restringida) --------------------------------

class _Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def _ver(self):
        return self.tokens[self.pos]

    def _comer(self, tipo):
        t = self._ver()
        if t.tipo != tipo:
            raise ValueError("expresión inválida o paréntesis no balanceados")
        self.pos += 1
        return t

    # expr := frac
    def expr(self):
        return self.frac()

    # frac := power ( '/' power )*
    def frac(self):
        nodo = self.power()
        while self._ver().tipo == 'DIV':
            self._comer('DIV')
            derecha = self.power()
            nodo = ('DIV', nodo, derecha)
        return nodo

    # power := unary ( '^' power )?
    def power(self):
        base = self.unary()
        if self._ver().tipo == 'POW':
            self._comer('POW')
            exp = self.power()  # asociatividad derecha
            return ('POW', base, exp)
        return base

    # unary := '-' unary | primary
    def unary(self):
        if self._ver().tipo == 'MINUS':
            self._comer('MINUS')
            return ('NEG', self.unary())
        return self.primary()

    # primary := NUM | 'sqrt' '(' expr ')' | '(' expr ')'
    def primary(self):
        t = self._ver()
        if t.tipo == 'NUM':
            self._comer('NUM')
            return ('NUM', t.valor)
        if t.tipo == 'SQRT':
            self._comer('SQRT')
            self._comer('LPAREN')
            e = self.expr()
            self._comer('RPAREN')
            return ('SQRT', e)
        if t.tipo == 'LPAREN':
            self._comer('LPAREN')
            e = self.expr()
            self._comer('RPAREN')
            return e
        raise ValueError("expresión escalar inválida")


# --- Evaluación segura -------------------------------------------------------

def _a_numero(token_valor):
    # Si hay punto decimal -> float; si no -> int
    if '.' in token_valor:
        return float(token_valor)
    return int(token_valor)


def _es_entero(v):
    return isinstance(v, int) or (isinstance(v, Fraction) and v.denominator == 1)


def _a_fraction(v):
    if isinstance(v, Fraction):
        return v
    if isinstance(v, int):
        return Fraction(v, 1)
    raise TypeError("no convertible a Fraction")


def _evaluar(nodo):
    tipo = nodo[0]
    if tipo == 'NUM':
        return _a_numero(nodo[1])
    if tipo == 'NEG':
        val = _evaluar(nodo[1])
        return -val
    if tipo == 'SQRT':
        val = _evaluar(nodo[1])
        return math.sqrt(float(val))
    if tipo == 'DIV':
        izq = _evaluar(nodo[1])
        der = _evaluar(nodo[2])
        # Validar denominador 0
        if (isinstance(der, Fraction) and der == 0) or (
            isinstance(der, (int, float)) and der == 0
        ):
            raise ValueError("denominador 0 en fracción")
        # Reglas de tipo: si hay float -> float; si ambos son enteros/fracciones -> Fraction
        if isinstance(izq, float) or isinstance(der, float):
            return float(izq) / float(der)
        # Convertir a Fraction para mantener exactitud
        return _a_fraction(izq) / _a_fraction(der)
    if tipo == 'POW':
        base = _evaluar(nodo[1])
        exp = _evaluar(nodo[2])
        # Si exponente es entero -> potencia exacta si base es Fraction/int
        if _es_entero(exp):
            exp_int = int(exp) if not isinstance(exp, int) else exp
            if isinstance(base, float):
                return float(base) ** exp_int
            # base entero/fracción -> mantener Fraction si es posible
            base_frac = _a_fraction(base)
            return base_frac ** exp_int
        # Exponente fraccionario/no entero -> a float
        # Casos no soportados: base negativa con exponente no entero (complejos)
        if (isinstance(base, (int, float)) and float(base) < 0) or (
            isinstance(base, Fraction) and base < 0
        ):
            raise ValueError("exponente fraccionario sobre base negativa no soportado")
        return float(base) ** float(exp)
    raise ValueError("nodo inválido")


# --- Funciones públicas -------------------------------------------------------

def parse_scalar(text):
    """Convierte un texto a un número (int, float o Fraction).

    Soporta combinaciones anidadas de fracciones, potencias (asociativas a la
    derecha) y sqrt. No admite suma/resta binaria. El signo negativo unario sí.
    """
    if not text or not text.strip():
        raise ValueError("texto vacío")
    texto = _limpiar(text)
    tokens = _tokenizar(texto)
    parser = _Parser(tokens)
    arbol = parser.expr()
    # Debe consumirse todo
    if parser._ver().tipo != 'EOF':
        raise ValueError("expresión extra al final")
    return _evaluar(arbol)


def parse_vector(text):
    """Convierte un texto de vector a una lista de números.

    Ejemplo: "[1/2, -3, 0.25]" devuelve [Fraction(1,2), -3, 0.25].
    """
    if not text or not text.strip():
        raise ValueError("texto vacío")
    t = text.strip()
    if not (t.startswith('[') and t.endswith(']')):
        raise ValueError("vector debe iniciar con '[' y terminar con '']'")
    inner = t[1:-1].strip()
    if inner == '':
        return []
    # Separar por comas nivel 0 (sin corchetes internos ni paréntesis desbalanceados)
    items = []
    current = []
    depth_paren = 0
    depth_brack = 0
    for ch in inner:
        if ch == '[':
            depth_brack += 1
        elif ch == ']':
            depth_brack -= 1
        elif ch == '(':
            depth_paren += 1
        elif ch == ')':
            depth_paren -= 1
        if ch == ',' and depth_paren == 0 and depth_brack == 0:
            items.append(''.join(current).strip())
            current = []
        else:
            current.append(ch)
    if current:
        items.append(''.join(current).strip())
    result = [parse_scalar(it) for it in items if it]
    return result


def parse_matrix(text):
    """Convierte texto de matriz ([[...],[...],...]) a lista de listas numéricas.

    Verifica que todas las filas tengan la misma longitud.
    """
    if not text or not text.strip():
        raise ValueError("texto vacío")
    t = text.strip()
    if not (t.startswith('[') and t.endswith(']')):
        raise ValueError("matriz debe iniciar con '[' y terminar con '']'")

    # Quitar corchetes externos y procesar filas
    inner = t[1:-1].strip()
    if inner == '':
        return []

    rows_raw = []
    current = []
    depth_paren = 0
    depth_brack = 0
    for ch in inner:
        if ch == '[':
            depth_brack += 1
        elif ch == ']':
            depth_brack -= 1
        elif ch == '(':
            depth_paren += 1
        elif ch == ')':
            depth_paren -= 1
        if ch == ',' and depth_paren == 0 and depth_brack == 0:
            rows_raw.append(''.join(current).strip())
            current = []
        else:
            current.append(ch)
    if current:
        rows_raw.append(''.join(current).strip())

    # Cada fila debe ser un vector válido
    rows = []
    width = None
    for r in rows_raw:
        r = r.strip()
        if not r.startswith('[') or not r.endswith(']'):
            raise ValueError(f"fila inválida: '{r}'")
        vec = parse_vector(r)
        if width is None:
            width = len(vec)
        elif len(vec) != width:
            raise ValueError("filas con longitudes distintas")
        rows.append(vec)

    return rows

__all__ = [
    'parse_scalar',
    'parse_vector',
    'parse_matrix',
]
