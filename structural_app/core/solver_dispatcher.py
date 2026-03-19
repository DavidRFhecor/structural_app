import importlib
from typing import Any
from ..shared.domain.result_models import SolverResponse

class SolverDispatcher:
    """Orquestador que localiza y ejecuta el adaptador del formulario."""

    @staticmethod
    async def dispatch(form_key: str, dto: Any) -> SolverResponse:
        """
        Busca el adaptador dinámicamente y ejecuta el cálculo.
        """
        try:
            # Importación dinámica del adaptador del formulario
            module_path = f"structural_app.forms.{form_key}.adapter"
            adapter_module = importlib.import_module(module_path)
            
            # Todos los adaptadores deben tener una función 'calculate_element'
            # que reciba el DTO y devuelva un SolverResponse
            result = await adapter_module.calculate_element(dto)
            return result
            
        except Exception as e:
            # Aquí centralizamos el error para que la UI no muera
            return SolverResponse(
                is_ok=False,
                checks=[],
                summary=f"Error crítico en el solver: {str(e)}",
                metadata={"error": "true"}
            )