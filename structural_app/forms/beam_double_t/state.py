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
            
            # 1. Guardamos las capacidades (vienen en kNm desde el adapter)
            self.m_rd = float(scalars.get("m_rd", 0.0))
            self.v_rd = float(scalars.get("v_rd", 0.0))
            
            # 2. Calculamos el ratio REAL (Med y MRd deben estar en las mismas unidades, kNm)
            if self.m_rd > 0:
                # Ratio simple (0.34) -> Lo multiplicamos por 100 para el porcentaje (34.30)
                raw_ratio = (self.med / self.m_rd) * 100
                self.util_m = round(raw_ratio, 2)
            else:
                self.util_m = 0.0

            if self.v_rd > 0:
                raw_ratio_v = (self.ved / self.v_rd) * 100
                self.util_v = round(raw_ratio_v, 2)
            else:
                self.util_v = 0.0
                
                self.is_calculating = False

    @rx.event
    def on_load(self):
        self.is_calculating = False