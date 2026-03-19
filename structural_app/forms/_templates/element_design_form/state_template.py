import reflex as rx
from ....core.base_state import BaseState
from ....core.solver_dispatcher import SolverDispatcher
from .dto import ElementDTO

class ElementState(BaseState):
    # Variables de entrada (deben coincidir con config.json)
    ancho: float = 300.0
    canto: float = 500.0
    
    # Resultados (SolverResponse)
    results: any = None

    async def calculate(self):
        self.is_calculating = True
        yield # Actualiza la UI para mostrar el spinner
        
        dto = ElementDTO(
            ancho=self.ancho,
            canto=self.canto
        )
        
        # Despacho automático vía core
        self.results = await SolverDispatcher.dispatch(self.current_form_key, dto)
        self.is_calculating = False