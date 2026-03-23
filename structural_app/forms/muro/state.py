import reflex as rx
import plotly.graph_objects as go
from typing import Optional, Dict, Any
from structural_app.core.base_state import BaseState
from structural_app.shared.domain.result_models import SolverResponse
from structural_app.core.solver_dispatcher import SolverDispatcher

class MuroState(BaseState):
    # --- Inputs en Metros ---
    h_muro: float = 4.5
    e_superior: float = 0.30
    e_inferior: float = 0.50
    b_zapata: float = 3.0
    c_puntera: float = 1.0
    h_zapata: float = 0.60
    
    # Materiales
    fck: float = 25.0
    fyk: float = 500.0
    ned: float = 0.0

    # --- Resultados ---
    results: Optional[SolverResponse] = SolverResponse(
        is_ok=True, checks=[], summary="Esperando cálculo..."
    )

    @rx.event
    def on_load(self):
        """Crucial: Esto activa los campos al entrar en la página."""
        self.current_form_key = "muro"  # <--- Asegúrate de que coincida con el config.json
        self.is_calculating = False

    @rx.var
    def model_3d_payload(self) -> Dict[str, Any]:
        """Datos para el visor 3D."""
        return {
            "altura": self.h_muro,
            "espesor": self.e_inferior,
            "zapata_vuelo_puntera": self.c_puntera,
            "zapata_vuelo_talon": round(self.b_zapata - self.c_puntera - self.e_inferior, 2),
            "zapata_canto": self.h_zapata
        }

    @rx.event
    def calculate(self):
        """Ejecuta el cálculo."""
        self.is_calculating = True
        yield
        
        payload = {
            "h_muro": self.h_muro, 
            "e_superior": self.e_superior, 
            "e_inferior": self.e_inferior,
            "b_zapata": self.b_zapata, 
            "c_puntera": self.c_puntera, 
            "h_zapata": self.h_zapata,
            "fck": self.fck,
            "fyk": self.fyk,
            "ned": self.ned
        }
        
        # Llamada centralizada al SolverDispatcher
        raw_result = SolverDispatcher.dispatch_calculation("muro", payload)
        
        if isinstance(raw_result, SolverResponse):
            self.results = raw_result
        else:
            self.results = SolverResponse(is_ok=False, summary="Error en el motor de cálculo.")
            
        self.is_calculating = False
    
    @rx.var
    def muro_figure(self) -> go.Figure:
        """Genera la figura de Plotly reactivamente."""
        h = self.h_muro
        e = self.e_inferior
        p = self.c_puntera
        t = max(0.1, self.b_zapata - self.c_puntera - self.e_inferior)
        hz = self.h_zapata

        fig = go.Figure()

        # Caja de la Zapata
        fig.add_trace(go.Mesh3d(
            x=[0, p+e+t, p+e+t, 0, 0, p+e+t, p+e+t, 0],
            y=[0, 0, 1, 1, 0, 0, 1, 1],
            z=[0, 0, 0, 0, hz, hz, hz, hz],
            i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
            j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
            k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
            color='lightgrey', opacity=0.5
        ))

        # Caja del Fuste
        fig.add_trace(go.Mesh3d(
            x=[p, p+e, p+e, p, p, p+e, p+e, p],
            y=[0, 0, 1, 1, 0, 0, 1, 1],
            z=[hz, hz, hz, hz, hz+h, hz+h, hz+h, hz+h],
            i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
            j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
            k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
            color='grey', opacity=0.8
        ))

        fig.update_layout(
            scene=dict(xaxis_title='X (m)', yaxis_title='Ancho (m)', zaxis_title='Z (m)', aspectmode='data'),
            margin=dict(r=0, l=0, b=0, t=0),
            showlegend=False,
            height=400
        )
        return fig