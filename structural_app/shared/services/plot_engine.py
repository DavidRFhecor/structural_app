import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from structural_app.shared.domain.constants import COLOR_PRIMARY

class PlotEngine:
    """Motor central de visualización de FHECOR para una arquitectura de cero esfuerzo."""

    @staticmethod
    def create_mixed_view(wants_3d: bool, wants_2d: bool):
        """
        Gestiona la creación de la figura según las necesidades del JSON.
        Devuelve la figura y las coordenadas (columna_3d, columna_2d).
        """
        if wants_3d and wants_2d:
            # Escenario A: Vista doble (3D Izquierda, 2D Derecha)
            fig = make_subplots(
                rows=1, cols=2, 
                specs=[[{"type": "scene"}, {"type": "xy"}]],
                subplot_titles=("Modelo 3D", "Análisis Seccional")
            )
            return fig, (1, 2)
        
        # Escenario B: Vista única (o ninguna)
        fig = go.Figure()
        return fig, (None, None)

    @staticmethod
    def apply_standard_layout(fig, title: str = "Análisis Estructural"):
        """
        Aplica el libro de estilo corporativo de FHECOR a cualquier gráfico de Plotly.
        """
        fig.update_layout(
            template="plotly_white",
            title=title,
            height=400,
            margin=dict(l=20, r=20, b=20, t=50),
            legend=dict(
                orientation="h", 
                yanchor="bottom", 
                y=1.02, 
                xanchor="right", 
                x=1
            ),
            font=dict(family="Inter", size=12),
            # Forzamos que el fondo sea limpio para reportes
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )
        
        # Serialización segura para evitar que Reflex falle con datos de Numpy
        return json.loads(fig.to_json())

    @staticmethod
    def get_interaction_style():
        """Devuelve el diccionario de estilo para trazados de capacidad."""
        return dict(
            fill='tozeroy',
            fillcolor='rgba(0, 85, 150, 0.1)', # COLOR_PRIMARY con transparencia
            line=dict(color=COLOR_PRIMARY, width=2)
        )