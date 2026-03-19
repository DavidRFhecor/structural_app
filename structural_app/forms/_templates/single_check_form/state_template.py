import reflex as rx
from ....core.base_state import BaseState
from .adapter import calculate_element

class SingleCheckState(BaseState):
    valor_ed: float = 0.0
    results: any = None

    async def calculate(self):
        self.is_calculating = True
        yield
        # En formularios simples, podemos llamar al adaptador directamente o vía dispatcher
        from .dto import SimpleDTO
        dto = SimpleDTO(valor_ed=self.valor_ed)
        self.results = await calculate_element(dto)
        self.is_calculating = False