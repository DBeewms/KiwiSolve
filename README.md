# KiwiSolve — Guía general del proyecto y política de números (API 100% en español)

Proyecto cooperativo en Django para aprender y practicar Álgebra Lineal con una interfaz clara. Este documento resume cómo trabajar juntos y la filosofía numérica del proyecto a un nivel general.

## Qué es y por qué
- Explorar operaciones de vectores y matrices en la web.
- Mantener resultados consistentes gracias a una política numérica unificada.
- Priorizar claridad pedagógica: código y mensajes en español, UI simple.

## Requisitos rápidos
- Python 3.10+
- Django 5.x
- Entorno virtual (recomendado)
- Dependencias en `requirements.txt` (incluye `django-environ`).

## Puesta en marcha (Windows PowerShell)
```powershell
# 1) Crear y activar entorno
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2) Instalar dependencias
pip install -r requirements.txt

# 3) Variables de entorno
copy .env.example .env  # Ajusta SECRET_KEY, DEBUG, ALLOWED_HOSTS

# 4) Migraciones (si aplica)
python manage.py migrate

# 5) Ejecutar
python manage.py runserver
```

## Estructura del repositorio (resumen)
```
apps/
  pages/      # Página de inicio y rutas generales
  algebra/    # Próximas operaciones de álgebra (servicios en services/)
core/
  number_mode.py   # Política de números unificada (ver sección abajo)
  parse.py         # Parser seguro de texto a números, vectores y matrices
  format.py        # Formateo legible de escalares y matrices (auto fracción/decimal)
  validate.py      # Validaciones de dimensiones y precondiciones (fail-fast)
  utils.py         # Utilidades compartidas (secuencia/matriz, normalización)
  matrix_utils.py  # Primitivas de matrices (ceros, identidad, copiar, aumentar, dividir_aumentada, ...)
  steps.py         # Trazabilidad pedagógica opcional (Steps)
config/            # settings/urls/wsgi/asgi
static/            # css/js/img (incluye toggle de tema)
templates/         # base.html + partials (_header, _footer)
```

## Política de números (visión general)
El archivo `core/number_mode.py` define cómo representamos y comparamos números en todo el proyecto. La idea es evitar sorpresas al mezclar decimales, fracciones y entradas de texto.

- Modos disponibles:
  - `fraction` (predeterminado): exactitud racional con `fractions.Fraction`.
  - `float`: valores en punto flotante con redondeo y tolerancia.
- Conversión segura de cadenas: soporta `"a/b"`, `"3.14"`, `"1e-3"`, etc.
- Comparaciones: usar la API del módulo en lugar de `==` cuando se trabaje con floats.
- API legible exclusivamente en español (sin alias en inglés para evitar mezcla de estilos).

Uso típico (muy resumido):
```python
from core import configurar_modo_numerico, convertir_a_numero, son_iguales

# Modo exacto por defecto
a = convertir_a_numero("3/4")         # Fraction(3, 4)

# Cambiar a float con redondeo/tolerancia
configurar_modo_numerico("float", decimales=4, tolerancia=1e-9)
son_iguales(0.1 + 0.2, 0.3)           # True (comparación tolerante)
```


## Flujo completo de datos (core pipeline)
El núcleo sigue una secuencia clara para transformar entrada de usuario en resultados confiables:

1. Entrada textual (formulario, campo web) -> `parse.py`
  - `parsear_escalar`, `parsear_vector`, `parsear_matriz` convierten cadenas restringidas a tipos nativos (`int`, `float`, `Fraction`).
  - Reglas estrictas: fracciones, potencias con `^`, raíz `sqrt(...)`, paréntesis y signo negativo unario. Sin sumas/restas binarias.
  - Errores en español (ValueError) si la sintaxis es inválida.

2. Conversión al modo numérico -> `number_mode.py`
  - Funciones: `convertir_a_numero` y `convertir_a_matriz`.
  - Decide según modo global (`fraction` o `float`) cómo representar internamente.
  - En modo `float` aplica redondeo y tolerancia para comparaciones (`son_iguales`).

3. Validación estructural / precondiciones -> `validate.py`
  - `asegurar_rectangular`, `asegurar_cuadrada`, `asegurar_multiplicable`, `asegurar_aumentada` para matrices.
  - `asegurar_intervalo`, `asegurar_cambio_signo` para algoritmos numéricos (p.ej. bisección).
  - Fallos rápidos con mensajes claros (ValueError).

4. Operación algebraica / numérica (futuro en `apps/algebra/services/`)
  - Ejemplos planeados: producto de matrices, determinante, eliminación gaussiana, métodos iterativos.
  - Cada servicio debe llamar primero a validaciones y luego usar representación del modo numérico.
  - Para operaciones de bajo nivel sobre filas/columnas, usar `core/matrix_utils.py`.

5. Formateo para salida -> `format.py`
  - `formatear_escalar`: en `auto`, si la fracción tiene decimal finito se muestra como decimal recortado; si no, fracción `a/b`.
  - Modos forzados: `fraction`, `float`.
  - `formatear_matriz` aplica `formatear_escalar` elemento a elemento y normaliza a 2D.

6. Render / UI
  - Los strings formateados llegan a templates para mostrar resultados consistentes.

### Ejemplo encadenado (mini flujo)
```python
from core import parsear_escalar, convertir_a_numero, asegurar_cuadrada, formatear_matriz

texto = "(3/2)^(2)"          # 9/4 exacto
valor_nativo = parsear_escalar(texto)          # Fraction(9,4)
valor_modo = convertir_a_numero(valor_nativo)  # Fraction(9,4) (modo fraction por defecto)
asegurar_cuadrada([[valor_modo]])              # Matriz 1x1 es cuadrada
salida = formatear_matriz([[valor_modo]])      # [["2.25"]] (decimal finito)
```

### Decisiones de diseño
- Separación de responsabilidades: parse (texto) / number_mode (representación) / validate (precondición) / format (presentación).
- Fail-fast: evitar trabajar sobre datos mal formados o dimensiones incorrectas.
- Legibilidad: funciones y mensajes en español; sin anotaciones tipo `->` en la API para reducir ruido al aprendizaje.
- Exactitud vs rendimiento: fracciones para precisión; flotantes sólo cuando el usuario lo configure.

### Errores típicos y origen
| Error | Módulo | Causa |
|-------|--------|-------|
| "carácter no permitido" | parse.py | Token inválido en entrada textual |
| "A debe ser cuadrada" | validate.py | Matriz no cumple nfilas == ncols |
| "modo debe ser 'fraction' o 'float'" | number_mode.py | Configuración inválida |
| "tipo no soportado para formato automático" | format.py | Escalar de tipo inesperado |

## Referencia rápida de funciones core

| Archivo | Función | Propósito resumido |
|---------|---------|--------------------|
| parse.py | parsear_escalar | Texto -> número nativo seguro |
| parse.py | parsear_vector | Texto -> lista de números |
| parse.py | parsear_matriz | Texto -> matriz de números |
| number_mode.py | configurar_modo_numerico | Seleccionar modo global |
| number_mode.py | convertir_a_numero | Adaptar escalar/vector al modo |
| number_mode.py | convertir_a_matriz | Adaptar a matriz modo-activa |
| number_mode.py | son_iguales | Comparación tolerante/exacta |
| number_mode.py | es_cero | Chequeo de cero según modo |
| number_mode.py | es_uno | Chequeo de uno según modo |
| validate.py | asegurar_rectangular | Verifica forma rectangular |
| validate.py | asegurar_cuadrada | Verifica cuadrada |
| validate.py | asegurar_multiplicable | Compatibilidad multiplicación |
| validate.py | asegurar_aumentada | Forma aumentada Ax=b |
| validate.py | asegurar_intervalo | Verifica a < b |
| validate.py | asegurar_cambio_signo | Cambio de signo (bisección) |
| utils.py | es_secuencia / es_matriz | Detección de colecciones/matriz 2D |
| utils.py | normalizar_a_matriz | Reestructurar escalar/1D/2D a 2D |
| format.py | formatear_escalar | Formato humano (auto/fraction/float) |
| format.py | formatear_matriz | Matriz de cadenas formateadas |
| matrix_utils.py | ceros | Crea matriz m×n de ceros |
| matrix_utils.py | identidad | Matriz identidad n×n |
| matrix_utils.py | copiar | Copia profunda de matriz |
| matrix_utils.py | aumentar | Concatena horizontalmente [A | B] |
| matrix_utils.py | dividir_aumentada | Parte [A | B] en (A, B) |
| matrix_utils.py | intercambiar_filas | Intercambia filas i y j |
| matrix_utils.py | escalar_fila | F_i ← c · F_i |
| matrix_utils.py | sumar_multiplo_fila | F_i ← F_i + c · F_j |
| matrix_utils.py | buscar_fila_pivote | Busca fila con pivote no nulo |
| steps.py | Steps (begin/add/end) | Registro pedagógico opcional de pasos |

### Registro pedagógico opcional (Steps)
El módulo `core/steps.py` permite capturar una secuencia de pasos para explicar operaciones.

Ejemplo rápido:
```python
from core import Steps, asegurar_cuadrada, formatear_matriz

steps = Steps()
steps.begin("determinante")
steps.add("validar matriz", {"n": 2})
asegurar_cuadrada([[1,2],[3,4]])
steps.add("expansión menor (demo)", {"fila":0})
steps.end({"resultado": "ejemplo"})

print(steps.to_list())
# [
#   {"op": "determinante", "state": {}, "etapa": "inicio", ...},
#   {"op": "determinante", "state": {"n": 2}, "etapa": "paso", "msg": "validar matriz", ...},
#   {"op": "determinante", "state": {"fila": 0}, "etapa": "paso", ...},
#   {"op": "determinante", "state": {"resultado": "ejemplo"}, "etapa": "fin", ...}
# ]
```

Las funciones públicas podrán (en el futuro) aceptar un parámetro opcional `steps: Steps | None` para registrar su progreso sin obligar a la UI a mostrarlo.

### Primitivas de matrices (matrix_utils)
Utilidades atómicas para construir y manipular matrices sin mutar las entradas. Todas validan estructura y lanzan errores claros en español.

Ejemplo rápido:
```python
from core import (
  ceros, identidad, copiar, aumentar, dividir_aumentada,
  intercambiar_filas, escalar_fila, sumar_multiplo_fila, buscar_fila_pivote,
  configurar_modo_numerico
)

configurar_modo_numerico('fraction')
A = ceros(2, 3)                 # [[0,0,0],[0,0,0]]
I = identidad(3)                # 3x3
C = copiar(I)                   # copia profunda
AB = aumentar(I, [[10],[20],[30]])
A_part, B_part = dividir_aumentada(AB, 3)

M = [[1,2,3],[0,4,5],[0,0,6]]
M2 = intercambiar_filas(M, 0, 2)
M3 = escalar_fila(M, 1, 2)
M4 = sumar_multiplo_fila(M, 0, 1, -0.5)
fila = buscar_fila_pivote(M, col=1, fila_inicio=0)  # 0
```


## UI y temas
- Botón de tema claro/oscuro (manual) en el header.
- Preferencia persistida en `localStorage` (`ks-theme`).
- No se detecta el tema del sistema: la app inicia en claro por defecto.

## Convenciones de código (acuerdo de equipo)
- Idioma: español para nombres, docstrings y mensajes.
- Evitar sintaxis que distraiga al aprendizaje (no usar `->` de tipos en funciones públicas).
- Pequeñas funciones privadas con prefijo `_` y comentarios claros.
- Evitar lambdas en lógica central; preferir funciones con nombre.
- Reutilizar `core/number_mode.py` para toda conversión/comparación numérica.

## Flujo de trabajo colaborativo
- Rama principal: `main` (protegida).
- Ramas de trabajo: `feat/<nombre>`, `fix/<nombre>`, `docs/<nombre>`.
- Pull Requests:
  - Descripción breve del “qué” y “por qué”.
  - Referenciar issue si aplica.
  - Checklist de verificación (correr servidor local, revisar UI, validar funciones clave).
- Commits (recomendado): `feat: ...`, `fix: ...`, `docs: ...`, `refactor: ...`, `style: ...`.
- Issues y tareas: etiquetar con `type`, `area` (p.ej. `area:number_mode`, `area:ui`).

## Tests (sugerido)
- Framework: `pytest`/`pytest-django` (pendiente de integrar).
- Empezar por casos del módulo numérico: conversiones, igualdad tolerante, matrices 1x1/1xN/2D.
- Añadir pruebas de vistas cuando se implementen operaciones de álgebra.

## Configuración y entorno
- `config/settings.py` usa `django-environ` y `.env`.
- Ajusta `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS` en `.env`.

## Próximos pasos
- Suite de tests para `core/number_mode.py`.
- Refactor utilidades comunes (core/utils) para reducir duplicación.
- Primeros servicios en `apps/algebra/services/` (producto de matrices, determinante, etc.).
- Página de ejemplos interactivos.

