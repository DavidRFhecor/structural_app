import reflex as rx
from structural_app.core.base_state import BaseState
from structural_app.core.solver_dispatcher import SolverDispatcher

class BeamDoubleTState(BaseState):
    """Estado específico para el cálculo de viga doble T."""
    # Inputs Geométricos
    h: float = 1200.0
    b_top: float = 600.0
    t_top: float = 150.0
    b_bot: float = 400.0
    t_bot: float = 150.0
    tw: float = 120.0
    
    # Materiales y Cargas
    fck: float = 35.0
    med: float = 500.0
    ved: float = 200.0

    # Resultados de salida
    m_rd: float = 0.0
    v_rd: float = 0.0
    util_m: float = 0.0
    util_v: float = 0.0

    def run_calculation(self):
        self.is_calculating = True
        
        # Empaquetado de datos para el Dispatcher
        payload = {
            "h": self.h, "b_top": self.b_top, "t_top": self.t_top,
            "b_bot": self.b_bot, "t_bot": self.t_bot, "tw": self.tw,
            "fck": self.fck, "med": self.med, "ved": self.ved
        }
        
        # El dispatcher se encarga de buscar el adaptador correcto
        result = SolverDispatcher.dispatch_calculation("beam_double_t", payload)
        
        if result.get("success"):
            scalars = result["scalars"]
            self.m_rd = scalars.get("m_rd", 0.0)
            self.v_rd = scalars.get("v_rd", 0.0)
            self.util_m = scalars.get("util_m", 0.0)
            self.util_v = scalars.get("util_v", 0.0)
        
        self.is_calculating = False