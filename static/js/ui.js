// ui.js – utilidades pequeñas de UI
// Funcionalidades actuales:
//  - Copiar matrices resultado al portapapeles usando botones con atributo data-copy-matrix
//    El atributo debe contener un selector CSS que apunte a un elemento <pre> oculto
//    donde está la matriz serializada.
//  - Fallback para navegadores sin navigator.clipboard.
//
// Extensiones futuras sugeridas:
//  - Navegación con flechas entre celdas de matrices.
//  - Resaltado temporal al copiar (toast / aria-live).
//  - Validación inmediata por blur (aplicación de clases .error a inputs).
(function(){
  function copyTextFromSelector(sel){
    var el = document.querySelector(sel);
    if(!el) return;
    var text = el.textContent || '';
    if(navigator.clipboard && navigator.clipboard.writeText){
      navigator.clipboard.writeText(text).catch(function(){});
      return;
    }
    // Fallback
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.left = '-9999px';
    document.body.appendChild(ta);
    ta.focus(); ta.select();
    try { document.execCommand('copy'); } catch(_) {}
    document.body.removeChild(ta);
  }
  document.addEventListener('click', function(e){
    var btn = e.target.closest('[data-copy-matrix]');
    if(!btn) return;
    var target = btn.getAttribute('data-copy-matrix');
    if(target){ copyTextFromSelector(target); }
  });
})();
