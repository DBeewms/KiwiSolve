# Guía de estilos KiwiSolve

Esta guía documenta la organización de los archivos CSS y cómo extenderlos de forma limpia.

## Estructura
```
static/
  css/
    kiwisolve.css          # Design tokens (colores, tipografía, sombras, radios)
    base.css               # Reset mínimo + reglas globales
    layout.css             # Primitivas de layout (header, nav, contenedores)
    components/
      buttons.css          # Componente de botones reutilizable
    themes/
      kiwisolve-dark.css   # Overrides manuales para modo oscuro
  img/
    KiwiSolveLogo.png      # Logo oficial provisto por el proyecto
```

## Orden de carga recomendado
1. `kiwisolve.css`
2. `base.css`
3. `layout.css`
4. Componentes (`buttons.css`, futuros `forms.css`, etc.)
5. Tema opcional (`themes/kiwisolve-dark.css` si quieres forzar modo oscuro)

## Variables clave (`kiwisolve.css`)
Prefijo: `--ks-` para evitar colisiones.
- Colores de marca: `--ks-color-sky`, `--ks-color-grape`, `--ks-color-royal-purple`, `--ks-color-violet-blue`, `--ks-color-savoy`
- Superficie y texto: `--ks-color-bg`, `--ks-color-text`, `--ks-color-muted`, `--ks-color-border`
- Radios: `--ks-radius-xs|sm|md|lg`
- Sombras: `--ks-shadow-sm|md|lg`
- Tipografía base: `--ks-font-sans`

## Logo
Este proyecto ya incluye el logotipo oficial en `static/img/KiwiSolveLogo.png` y se usa en las plantillas.
Si tu instalación necesita otra escala, ajusta los tamaños desde CSS (por ejemplo en `.hero .logo img` o clases específicas) sin reemplazar el archivo.

## Crear un nuevo componente
1. Crea archivo en `static/css/components/<nombre>.css`.
2. Usa variables existentes; si requieres nuevas, agrégalas en `kiwisolve.css`.
3. Documenta en la cabecera del archivo propósito y cómo se usan las clases.
4. Importa el CSS en la plantilla (o en un bundle futuro) después de `layout.css`.

## Modo oscuro
Política actual: inicio siempre en modo claro. El usuario cambia manualmente.

- Manual: el toggle (JS) añade `data-theme="dark"` y la clase `dark` al `<html>`.
- Overrides: `themes/kiwisolve-dark.css` o las variables dentro de `kiwisolve.css` bajo el selector `html[data-theme='dark'], html.dark`.
- Sin detección automática: se eliminó `@media (prefers-color-scheme: dark)` para evitar que el sistema fuerce el modo. Si quieres reactivarlo, agrega nuevamente el media query (ver historial git) o detecta en JS y sólo usarlo para elegir el primer valor (sin escuchar cambios).

Buenas prácticas al extender modo oscuro:
1. Ajusta sólo superficies y texto, conserva colores de marca (evita saturarlos demasiado).
2. Verifica contraste mínimo (WCAG AA: 4.5:1 para texto normal, 3:1 para grande).
3. No relies en filtros invert, usa variables.

## Buenas prácticas
- No dupliques colores directos: usa variables de `:root`.
- Mantén nombres semánticos (evitar `.blue-button`, preferir `.button.secondary`).
- Documenta cada archivo con un bloque de comentario inicial.
- Evita !important; si lo necesitas, revisa especificidad primero.
- Revisa contraste (WCAG) cuando cambies paleta o fondo.

## Próximas extensiones sugeridas
- `forms.css` para campos de entrada y validaciones visuales.
- `grid.css` para layout de matrices.
- `animations.css` para micro-interacciones (hover, focus).
- `themes/high-contrast.css` para accesibilidad extendida.

## Ejemplo de botón personalizado
```html
<a class="button" style="--_bg:#6A1B9A; --_bg-hover:#7E57C2" href="#">Acción personalizada</a>
```

## Limpieza y mantenimiento
- Antes de añadir una nueva variable, verifica que no exista una similar.
- Consolidar estilos duplicados en componentes reutilizables.
- Revalida que la cascada de importación conserva el diseño tras cambios.

---
Guía viva: actualiza este documento cuando agregues nuevos componentes o tokens.
