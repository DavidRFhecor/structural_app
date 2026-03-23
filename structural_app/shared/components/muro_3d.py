import reflex as rx

def muro_visualizer(figure_var) -> rx.Component:
    """Simplemente renderiza la figura de Plotly que recibe del State."""
    return rx.plotly(
        data=figure_var,
        height="400px",
        width="100%"
    )