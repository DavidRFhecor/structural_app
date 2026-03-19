from typing import Dict, Any
# Importamos los adaptadores de cada formulario
from structural_app.forms.cortante_circular import adapter as cortante_adapter
from structural_app.forms.beam_double_t import adapter as beam_adapter

class SolverDispatcher:
    @staticmethod
    def dispatch_calculation(form_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enruta la solicitud de cálculo al adaptador correspondiente.
        """
        try:
            if form_id == "cortante_circular":
                # Aquí llamamos a la función del adaptador de cortante
                return cortante_adapter.calculate_element(payload)
            
            elif form_id == "beam_double_t":
                # Aquí llamamos a la función del adaptador de viga doble T
                return beam_adapter.calculate_element(payload)
            
            else:
                return {
                    "success": False, 
                    "error": f"No se encontró un solver registrado para: {form_id}"
                }
        except Exception as e:
            return {
                "success": False, 
                "error": f"Error crítico en el Dispatcher: {str(e)}"
            }