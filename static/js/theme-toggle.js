/*
  theme-toggle.js – Control del modo claro/oscuro.
  Estrategia:
    - Usa class .dark en <html> para activar overrides.
    - Persiste preferencia en localStorage (clave: ks-theme).
    - Cambia icono (🌞 / 🌙) según estado.
  Accesibilidad:
    - Botón con aria-label descriptivo.
    - Icono marcado aria-hidden.
*/
(function(){
  const root = document.documentElement;
  const btn = document.getElementById('ks-theme-toggle');
  if(!btn) return;

  const apply = (mode) => {
    if (mode === 'dark') {
      root.setAttribute('data-theme', 'dark');
      root.classList.add('dark'); // compatibilidad con estilos previos
      btn.setAttribute('aria-checked', 'true');
      btn.title = 'Modo claro';
    } else {
      root.setAttribute('data-theme', 'light');
      root.classList.remove('dark');
      btn.setAttribute('aria-checked', 'false');
      btn.title = 'Modo oscuro';
    }
  };

  // Estado inicial: localStorage -> light (sin detectar preferencia del sistema)
  let stored = null;
  try { stored = localStorage.getItem('ks-theme'); } catch(_) {}
  if(!stored){ stored = 'light'; }
  apply(stored);

  btn.addEventListener('click', () => {
    const next = (root.getAttribute('data-theme') === 'dark') ? 'light' : 'dark';
    apply(next);
    try { localStorage.setItem('ks-theme', next); } catch(_) {}
  });
})();
