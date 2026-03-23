import importlib
from typing import Any, Dict
from structural_app.shared.domain.result_models import SolverResponse

class SolverDispatcher:
    """
    Despachador central que conecta los formularios con sus motores de cálculo
    usando importaciones dinámicas para evitar importaciones circulares.
    """
    
    # Mapa de rutas a los adaptadores
    ADAPTER_MAP = {
        "beam_double_t": "structural_app.forms.beam_double_t.adapter",
        "cortante_circular": "structural_app.forms.cortante_circular.adapter",
        "muro": "structural_app.forms.muro.adapter",
    }

    @staticmethod
    def dispatch_calculation(form_key: str, payload: Dict[str, Any]) -> SolverResponse:
        """
        Carga el adaptador bajo demanda y ejecuta el cálculo.
        """
        if form_key not in SolverDispatcher.ADAPTER_MAP:
            return SolverResponse(
                is_ok=False, 
                summary=f"Error: No existe adaptador para '{form_key}'"
            )

        try:
            # IMPORTACIÓN DINÁMICA: Solo importamos el adaptador cuando se necesita
            module_path = SolverDispatcher.ADAPTER_MAP[form_key]
            adapter_module = importlib.import_module(module_path)
            
            # Llamamos a la función calculate_element del adaptador
            if hasattr(adapter_module, "calculate_element"):
                return adapter_module.calculate_element(payload)
            else:
                return SolverResponse(
                    is_ok=False, 
                    summary=f"Error: El módulo {form_key} no tiene 'calculate_element'"
                )
                
        except Exception as e:
            return SolverResponse(
                is_ok=False, 
                summary=f"Error crítico en Dispatcher: {str(e)}"
            )