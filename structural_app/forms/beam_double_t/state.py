import reflex as rx
from typing import Any
from structural_app.core.base_state import BaseState
from structural_app.core.solver_dispatcher import SolverDispatcher

def safe_float(value: Any, default: float = 0.0) -> float:
    """Función auxiliar para convertir inputs de la UI a números reales."""
    try:
        if value is None or str(value).strip() == "" or str(value).strip() == "-":
            return default
        return float(value)
    except (ValueError, TypeError):
        return default

class BeamDoubleTState(BaseState):
    """Estado blindado contra errores de tipo de Reflex."""
    
    # --- Inputs Geométricos (Valores iniciales) ---
    h: float = 1200.0
    b_top: float = 600.0
    t_top: float = 150.0
    b_bot: float = 400.0
    t_bot: float = 150.0
    tw: float = 120.0
    
    # --- Materiales y Esfuerzos ---
    fck: float = 35.0
    med: float = 500.0
    ved: float = 200.0

    # --- Resultados ---
    m_rd: float = 0.0
    v_rd: float = 0.0
    util_m: float = 0.0
    util_v: float = 0.0

    # ==========================================================
    # ⚙️ SETTERS CON FILTRO DE SEGURIDAD
    # ==========================================================

    @rx.event
    def set_value(self, field: str, value: str):
        """Setter genérico: Sanitiza el string antes de asignarlo."""
        # Esta es la 'aduana': convertimos el texto a float real
        clean_val = safe_float(value)
        setattr(self, field, clean_val)

    @rx.event
    def set_h(self, value: str):
        """Setter específico para h (Canto)."""
        self.h = safe_float(value, default=1200.0)

    # ==========================================================
    # 🚀 LÓGICA DE CÁLCULO
    # ==========================================================

    @rx.event
    def run_calculation(self):
        """Llama al motor de cálculo con datos ya validados como floats."""
        self.is_calculating = True
        
        payload = {
            "h": self.h, "b_top": self.b_top, "t_top": self.t_top,
            "b_bot": self.b_bot, "t_bot": self.t_bot, "tw": self.tw,
            "fck": self.fck, "med": self.med, "ved": self.ved
        }
        
        result = SolverDispatcher.dispatch_calculation("beam_double_t", payload)
        
        if result.get("success"):
            scalars = result.get("scalars", {})
            # Forzamos float también al recibir para evitar que el dispatch meta strings
            self.m_rd = safe_float(scalars.get("m_rd"))
            self.v_rd = safe_float(scalars.get("v_rd"))
            self.util_m = safe_float(scalars.get("util_m"))
            self.util_v = safe_float(scalars.get("util_v"))
        
        self.is_calculating = False

    @rx.event
    def on_load(self):
        self.is_calculating = False