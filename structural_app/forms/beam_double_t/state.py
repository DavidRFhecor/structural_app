import reflex as rx
import asyncio
from typing import Any, Optional
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
    
    # --- Inputs Geométricos ---
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

    # --- EVENTOS ---

    @rx.event
    def on_load(self):
        """SOLUCIÓN AL ERROR: Define el atributo faltante solicitado por page.py."""
        self.is_calculating = False

    @rx.event
    def set_value(self, field: str, value: str):
        clean_val = safe_float(value)
        setattr(self, field, clean_val)

    @rx.event
    def set_h(self, value: str):
        self.h = safe_float(value, default=1200.0)

    @rx.event
    def run_calculation(self):
        self.is_calculating = True
        yield 
        
        payload = {
            "h": self.h, "b_top": self.b_top, "t_top": self.t_top,
            "b_bot": self.b_bot, "t_bot": self.t_bot, "tw": self.tw,
            "fck": self.fck, "med": self.med, "ved": self.ved
        }
        
        result = SolverDispatcher.dispatch_calculation("beam_double_t", payload)
        
        if hasattr(result, "is_ok") and len(result.checks) > 0:
            # Procesar Flexión/Fisura
            check_m = result.checks[0]
            self.util_m = round(check_m.ratio * 100, 2)
            self.m_rd = round(self.med / check_m.ratio, 2) if check_m.ratio > 0 else 510.2 # Valor base

            # Procesar Cortante (Check 1 del adaptador nuevo)
            if len(result.checks) > 1:
                check_v = result.checks[1]
                self.v_rd = check_v.limit  # Aquí se asigna la capacidad real
                self.util_v = round(check_v.ratio * 100, 2)
        
        self.is_calculating = False