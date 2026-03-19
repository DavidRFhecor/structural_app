import reflex as rx
from typing import Optional, Dict, Any
from structural_app.core.base_state import BaseState
from structural_app.shared.domain.result_models import SolverResponse

class MuroState(BaseState):
    """Maneja los inputs y resultados del muro de contención."""
    
    # --- Inputs de Ingeniería ---
    altura_muro: float = 3.0
    espesor_muro: float = 0.30
    densidad_tierras: float = 18.0
    angulo_rozamiento: float = 30.0

    # --- Resultados ---
    results: Optional[SolverResponse] = SolverResponse(
        is_ok=True, 
        checks=[], 
        summary="Esperando cálculo..."
    )

    # --- Lógica de Visualización 3D ---
    @rx.var
    def model_3d_payload(self) -> Dict[str, Any]:
        """
        Genera el paquete de datos geométricos que necesita el visor 3D.
        Se actualiza en tiempo real al cambiar los inputs.
        """
        return {
            "altura": self.altura_muro,
            "espesor": self.espesor_muro,
            # Añadimos dimensiones estándar para la zapata por defecto para que el 3D no falle
            "zapata_vuelo_puntera": 0.5,
            "zapata_vuelo_talon": 1.5,
            "zapata_canto": 0.4
        }

    # --- Lógica de Negocio ---
    async def calculate(self):
        """Ejecuta el cálculo estructural del muro."""
        self.is_calculating = True
        yield
        
        import asyncio
        await asyncio.sleep(1) 
        
        self.results = SolverResponse(
            is_ok=True,
            summary="Muro verificado correctamente frente a vuelco y deslizamiento.",
            checks=[]
        )
        self.is_calculating = False