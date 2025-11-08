# KiwiSolve — Guía general del proyecto y política de números

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
- API legible en español con alias en inglés para compatibilidad.

Uso típico (muy resumido):
```python
from core import number_mode as nm

# Modo exacto por defecto
a = nm.to_num("3/4")         # Fraction(3, 4)

# Cambiar a float con redondeo/tolerancia
nm.set_number_mode("float", decimales=4, tolerancia=1e-9)
nm.eq(0.1 + 0.2, 0.3)         # True (comparación tolerante)
```

> Nota: la documentación completa y ejemplos detallados están en `README_number_mode.md`.

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
- Primeros servicios en `apps/algebra/services/` (producto de matrices, determinante, etc.).
- Página de ejemplos interactivos.

