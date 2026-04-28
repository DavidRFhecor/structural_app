
import reflex as rx
from structural_app.shared.components.layout import main_layout
from structural_app.shared.components.form_renderer import render_dynamic_form
from structural_app.shared.components.result_cards import results_panel
from structural_app.core.base_state import BaseState
from .sketch_viewer import sketch_viewer

def generic_form_page():
    """Página genérica que usa el nombre correcto de la variable: active_form_config."""
    
    # Usamos el nombre real definido en tu BaseState
    config = BaseState.active_form_config

    return main_layout(
        rx.flex(
            # Panel Izquierdo: Formulario (40%)
            rx.box(
                render_dynamic_form(config, BaseState),
                sketch_viewer(BaseState),
                width={"sm": "100%", "lg": "40%"},
                padding="4",
                border_right={"sm": "none", "lg": "1px solid var(--gray-4)"},
            ),

            # Panel Derecho: Resultados (60%)
            rx.box(
                results_panel(BaseState),
                width={"sm": "100%", "lg": "60%"},
                padding="4",
            ),
            
            direction={"sm": "column", "lg": "row"},
            width="100%",
            spacing="4",
            align="start",
        ),
        state_class=BaseState 
    )