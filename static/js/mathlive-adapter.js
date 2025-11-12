/* mathlive-adapter.js
   Mejora progresiva: reemplaza inputs de celdas de matriz por <math-field>
   - Mantiene el <input type="text" name="..."> oculto, para que el POST funcione igual.
   - Convierte LaTeX <-> sintaxis soportada por el backend (a/b, sqrt(...), ^(...)).
*/
(function(){
  const ready = (fn) => {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  };

  // Conversión LaTeX -> Texto compatible con parser
  function latexToText(latex){
    if (!latex) return '';
    let s = String(latex);
    // Limpieza básica
    s = s.replace(/\\left|\\right/g, '');
    s = s.replace(/\\,/g, '');
    s = s.replace(/\s+/g, '');

    // fracciones: \frac{a}{b} -> (a)/(b)
    const frac = /\\frac\{([^{}]+)\}\{([^{}]+)\}/g;
    // reemplazar recursivamente por si hay anidadas
    while (frac.test(s)) {
      s = s.replace(frac, '($1)/($2)');
    }

    // sqrt{X} -> sqrt(X)
    const sqrt = /\\sqrt\{([^{}]+)\}/g;
    while (sqrt.test(s)) {
      s = s.replace(sqrt, 'sqrt($1)');
    }

    // potencias: ^{expr} -> ^(expr)
    s = s.replace(/\^\{([^{}]+)\}/g, '^(($1))');
    // potencias simples: ^2 -> ^(2)
    s = s.replace(/\^([\-]?[0-9]+(?:\.[0-9]+)?)/g, '($1)'); // first pass ensures ^(num)
    s = s.replace(/\^\(([^)]+)\)/g, '^($1)'); // normalize

    // Eliminar paréntesis redundantes alrededor de números simples
    s = s.replace(/\(([-]?\d+(?:\.\d+)?)\)/g, '$1');

    return s;
  }

  // Conversión Texto -> LaTeX (muy básico): a/b, sqrt(...), ^(...)
  function textToLatex(text){
    if (!text) return '';
    let s = String(text).trim();

    // sqrt(x) -> \sqrt{x}
    s = s.replace(/sqrt\(([^()]+)\)/g, '\\sqrt{$1}');

    // ^(expr) -> ^{expr}
    s = s.replace(/\^\(([^()]+)\)/g, '^{$1}');

    // fracciones simples a/b -> \frac{a}{b}
    // Intento conservador: no partir cuando hay múltiples '/'
    s = s.replace(/([^\s\/()]+)\s*\/\s*([^\s\/()]+)/g, '\\frac{$1}{$2}');

    return s;
  }

  function enhanceMatrixInputs(){
    // Sólo actuar si el custom element existe (MathLive cargado)
    if (!customElements.get('math-field')) return;

    const inputs = document.querySelectorAll('.matrix-grid input[type="text"]');
    inputs.forEach((inp) => {
      // Evitar duplicados
      if (inp.__mathfield) return;

    const mf = document.createElement('math-field');
      mf.className = 'math-cell';
    // Política oficial: controlar teclado con API (según docs)
    // Atributo equivalente: math-virtual-keyboard-policy="manual"
    mf.setAttribute('math-virtual-keyboard-policy', 'manual');
      mf.setAttribute('aria-label', inp.getAttribute('aria-label') || 'Celda');

      // Inicializar valor
      try {
        mf.value = textToLatex(inp.value || '');
      } catch (_) {
        mf.value = inp.value || '';
      }

      // Insertar antes del input y ocultar el input
      inp.parentNode.insertBefore(mf, inp);
      inp.style.display = 'none';

      // Sincronizar de math-field -> input (para POST)
      const sync = () => {
        try {
          const latex = mf.getValue ? mf.getValue() : mf.value;
          inp.value = latexToText(latex);
        } catch (_) {
          inp.value = mf.value || '';
        }
      };
      mf.addEventListener('input', sync);
      mf.addEventListener('change', sync);

      // Guardar referencia
      inp.__mathfield = mf;
    });

    // Asegurar sync antes de enviar el formulario
    document.querySelectorAll('form').forEach((form) => {
      form.addEventListener('submit', () => {
        const mfs = form.querySelectorAll('math-field');
        mfs.forEach((mf) => {
          const next = mf.nextElementSibling;
          if (next && next.tagName === 'INPUT') {
            try {
              next.value = latexToText(mf.getValue ? mf.getValue() : mf.value);
            } catch (_) {
              next.value = mf.value || '';
            }
          }
        });
      });
    });
  }

  // Insertar texto en un textarea a la posición del cursor
  function insertAtCursor(ta, text){
    if (!ta) return;
    const start = ta.selectionStart ?? ta.value.length;
    const end = ta.selectionEnd ?? ta.value.length;
    const before = ta.value.slice(0, start);
    const after = ta.value.slice(end);
    ta.value = before + text + after;
    const pos = start + text.length;
    if (ta.setSelectionRange) ta.setSelectionRange(pos, pos);
    ta.focus();
    // disparar evento input para frameworks/validaciones
    ta.dispatchEvent(new Event('input', { bubbles: true }));
  }

  function openMathEditorFor(targetSelector){
    const ta = document.querySelector(targetSelector);
    if (!ta) return;
    if (typeof Swal === 'undefined') {
      alert('Editor no disponible.');
      return;
    }
    const container = document.createElement('div');
    container.style.padding = '6px 0';
    const mf = document.createElement('math-field');
    mf.id = 'ml-modal';
    mf.setAttribute('math-virtual-keyboard-policy', 'manual');
    mf.style.minWidth = '360px';
    mf.style.minHeight = '44px';
    mf.style.display = 'block';
    container.appendChild(mf);

    Swal.fire({
      title: 'Editor matemático',
      html: container,
      showCancelButton: true,
      confirmButtonText: 'Insertar',
      cancelButtonText: 'Cancelar',
      didOpen: () => {
        try {
          // Prefill con selección o contenido completo
          const selStart = ta.selectionStart ?? 0;
          const selEnd = ta.selectionEnd ?? 0;
          const selectedText = selStart !== selEnd ? ta.value.slice(selStart, selEnd) : '';
          const seed = selectedText || ta.value || '';
          if (seed) mf.setValue ? mf.setValue(textToLatex(seed)) : (mf.value = textToLatex(seed));
          // Mostrar teclado y enfocar
          if (window.mathVirtualKeyboard) {
            window.mathVirtualKeyboard.show();
          }
          mf.focus();
        } catch(_) {}
      }
    }).then((res) => {
      if (res.isConfirmed) {
        try {
          const latex = mf.getValue ? mf.getValue() : mf.value;
          const text = latexToText(latex);
          insertAtCursor(ta, text);
          if (window.mathVirtualKeyboard) window.mathVirtualKeyboard.hide();
        } catch(_) {}
      } else {
        // Si se cancela, ocultar teclado
        if (window.mathVirtualKeyboard) window.mathVirtualKeyboard.hide();
      }
    });
  }

  function wireTextareaEditors(){
    document.querySelectorAll('.js-open-math-editor').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const sel = btn.getAttribute('data-target');
        if (!sel) return;
        openMathEditorFor(sel);
      });
    });
  }

  function wireTextareaShortcuts(){
    const areas = document.querySelectorAll('textarea');
    areas.forEach((ta) => {
      // Atajo de teclado: Ctrl+M abre el editor para el textarea enfocado
      ta.addEventListener('keydown', (ev) => {
        if ((ev.ctrlKey || ev.metaKey) && (ev.key === 'm' || ev.key === 'M')) {
          ev.preventDefault();
          if (ta.id) openMathEditorFor('#' + ta.id);
        }
      });
      // Doble clic abre el editor
      ta.addEventListener('dblclick', () => {
        if (ta.id) openMathEditorFor('#' + ta.id);
      });
    });
  }

  ready(() => {
    try {
  enhanceMatrixInputs();
  wireTextareaEditors();
  wireTextareaShortcuts();

      // Configuración global recomendada por docs
      const VK = window.mathVirtualKeyboard;
      if (VK) {
        // Teclado completo por defecto (según documentación: "default")
        VK.layouts = ["default"]; 
        // Tamaño/stack (se puede ajustar con CSS variables, ver más abajo)
        VK.visible = false;

        // Ajuste dinámico: expone la altura del teclado como variable CSS
        // y marca el body cuando el teclado está visible para poder adaptar la UI.
        try {
          VK.addEventListener?.("geometrychange", (ev) => {
            const h = ev?.detail?.boundingRect?.height || 0;
            document.body.style.setProperty('--vk-height', h + 'px');
            document.body.classList.toggle('vk-visible', h > 0);
          });
          VK.addEventListener?.("virtual-keyboard-toggle", (ev) => {
            const visible = !!(ev && ev.detail && ev.detail.visible);
            document.body.classList.toggle('vk-visible', visible);
            if (!visible) document.body.style.removeProperty('--vk-height');
            const b = document.getElementById('ml-kb-toggle');
            if (b) b.setAttribute('aria-pressed', visible ? 'true' : 'false');
          });
        } catch (_) {}
      }

      // Botón flotante para mostrar/ocultar el teclado virtual desde la API oficial
      const ensureKeyboardToggle = () => {
        if (document.getElementById('ml-kb-toggle')) return;

        const btn = document.createElement('button');
        btn.id = 'ml-kb-toggle';
        btn.type = 'button';
        btn.className = 'fab fab-kb';
        btn.setAttribute('aria-label', 'Mostrar/ocultar teclado matemático');
        btn.title = 'Teclado';
  btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="5" width="20" height="14" rx="2" ry="2"></rect><path d="M6 10h.01M10 10h.01M14 10h.01M18 10h.01M6 14h12"/></svg>';

        const ensureFocus = () => {
          const active = document.activeElement && document.activeElement.tagName === 'MATH-FIELD'
            ? document.activeElement
            : document.querySelector('math-field');
          if (active && active.focus) active.focus();
          return active;
        };

        btn.addEventListener('click', () => {
          const VK = window.mathVirtualKeyboard;
          const hasMathField = document.querySelector('math-field');
          if (hasMathField && VK) {
            const active = ensureFocus();
            if (!active) return;
            try {
              if (VK.visible) {
                VK.hide();
                btn.setAttribute('aria-pressed', 'false');
              } else {
                VK.show();
                btn.setAttribute('aria-pressed', 'true');
              }
            } catch(_) {}
            return;
          }
          // Si no hay math-field en la página, ofrecer editor sobre el textarea enfocado
          const focused = document.activeElement;
          if (focused && focused.tagName === 'TEXTAREA' && focused.id) {
            openMathEditorFor('#' + focused.id);
            return;
          }
          if (typeof Swal !== 'undefined') {
            Swal.fire({
              icon: 'info',
              title: 'Teclado matemático',
              text: 'Enfoca un campo o usa el botón "Editor (teclado)" para insertar una expresión.',
              timer: 1600,
              showConfirmButton: false
            });
          }
        });

        document.body.appendChild(btn);

        // Ocultar teclado al perder foco de todos los math-field (según guía)
        document.addEventListener('focusin', (e) => {
          if (e.target && e.target.tagName === 'MATH-FIELD') return;
          const VK = window.mathVirtualKeyboard;
          if (VK && VK.visible) VK.hide();
          const b = document.getElementById('ml-kb-toggle');
          if (b) b.setAttribute('aria-pressed', 'false');
        });
      };

      ensureKeyboardToggle();
    } catch(_) {}
  });
})();
