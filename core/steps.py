"""steps.py — Trazabilidad pedagógica opcional.

Propósito
---------
Permitir que las rutinas públicas registren (cuando el usuario lo pida) una
secuencia de pasos sencillos para explicar "qué está pasando" durante un
cálculo. Esto es útil a nivel didáctico y completamente opcional.

API pública
-----------
- Steps.begin(op_name)
- Steps.add(msg, state=None)
- Steps.end(result=None)

Convenciones
------------
- Estructura mínima por paso: {"op": str, "state": {…}}.
- Se permiten campos extra para enriquecer la explicación (por ejemplo
  "msg" o "etapa"), pero "op" y "state" siempre estarán presentes.
- Regla de uso: las funciones públicas de core pueden aceptar un parámetro
  opcional steps: Steps | None; si es None no se registra nada.

Notas
-----
- Este módulo no depende de Django.
- No hay formato rígido para "state"; debe ser un dict serializable.
- No se utiliza la sintaxis de retorno "->" para mantener consistencia de estilo.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime


class Steps:
    """Pequeño registrador de pasos pedagógicos.

    Uso típico:
        s = Steps()
        s.begin("producto_matrices")
        s.add("validar dimensiones", {"A": [2,3], "B": [3,2]})
        s.add("multiplicar fila x columna", {"i": 0, "j": 1})
        s.end({"resultado": "OK"})
        print(s.to_list())
    """

    def __init__(self):
        self._historial: List[Dict[str, Any]] = []
        self._op_actual: Optional[str] = None
        self._abierta: bool = False

    # ---------------- API principal -----------------
    def begin(self, nombre_operacion: str):
        """Comienza una nueva operación nombrada.

        Si ya hay una operación abierta, la cierra implícitamente antes
        de abrir la nueva (política simple para evitar estados extraños).
        """
        if self._abierta:
            # Cierre implícito de la operación anterior sin resultado
            self._agregar(etapa="fin", msg="cierre implícito")
        self._op_actual = str(nombre_operacion)
        self._abierta = True
        self._registrar_paso(etapa="inicio", msg="inicio")

    def add(self, mensaje: str, estado: Any | None = None):
        """Agrega un paso intermedio con un mensaje y estado opcional."""
        if not self._abierta:
            # Si no se llamó begin, abrimos una operación anónima
            self._op_actual = self._op_actual or "op_sin_nombre"
            self._abierta = True
            self._registrar_paso(etapa="inicio", msg="inicio implícito")
        self._registrar_paso(etapa="paso", msg=mensaje, state=estado)

    def end(self, resultado: Any | None = None):
        """Finaliza la operación actual registrando el resultado opcional."""
        if not self._abierta:
            # No hay operación activa: no hace nada
            return
        payload: Dict[str, Any] = {}
        if resultado is not None:
            # Guardamos el resultado dentro de state para mantener el contrato mínimo
            payload = {"resultado": resultado}
        self._registrar_paso(etapa="fin", msg="fin", state=payload)
        self._abierta = False
        self._op_actual = None

    # --------------- Utilidades ---------------------
    def to_list(self) -> List[Dict[str, Any]]:
        """Devuelve una copia del historial como lista de dicts."""
        return list(self._historial)

    def clear(self):
        """Limpia el historial."""
        self._historial.clear()
        self._op_actual = None
        self._abierta = False

    def __iter__(self):
        return iter(self._historial)

    def __len__(self):
        return len(self._historial)

    # --------------- Internas -----------------------
    def _registrar_paso(self, etapa: str, msg: Optional[str] = None, state: Any | None = None):
        """Inserta un paso en el historial normalizando la estructura mínima.

        Estructura base garantizada:
            {"op": <nombre>, "state": {…}}

        Campos adicionales útiles:
            - "etapa": "inicio" | "paso" | "fin"
            - "msg": texto humano opcional
            - "ts": ISO-8601 timestamp para trazabilidad
        """
        op = self._op_actual or ""
        # Normalizar state a dict (llamado 'estado' hacia afuera)
        if state is None:
            state_dict: Dict[str, Any] = {}
        elif isinstance(state, dict):
            state_dict = state
        else:
            state_dict = {"valor": state}

        paso: Dict[str, Any] = {
            "op": op,
            "state": state_dict,
            "etapa": etapa,
            "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        }
        if msg is not None:
            paso["msg"] = msg
        self._historial.append(paso)


__all__ = [
    "Steps",
]
