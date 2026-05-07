import reflex as rx
from structural_app.shared.components.layout import main_layout
# Importación corregida: usamos el nombre real de la función
from structural_app.shared.components.form_renderer import render_dynamic_form 
from structural_app.shared.components.result_cards import results_panel
from structural_app.core.base_state import BaseState
from .sketch_viewer import sketch_viewer

def generic_form_page():
    """Página con disposición 50/50 equilibrada."""
    config = BaseState.active_form_config

    return main_layout(
        rx.flex(
            # PANEL IZQUIERDO: Inputs + Sketch (50%)
            rx.box(
                rx.vstack(
                    render_dynamic_form(config, BaseState),
                    sketch_viewer(BaseState),
                    spacing="6",
                    width="100%",
                ),
                flex="1",  # Toma la mitad del espacio
                padding="4",
            ),

            # PANEL DERECHO: Resultados (50%)
            rx.box(
                results_panel(BaseState),
                flex="1",  # Toma la otra mitad del espacio
                padding="4",
                border_left={"lg": "1px solid #e5e7eb"}, # Línea divisoria sutil
            ),
            
            direction={"sm": "column", "lg": "row"},
            width="100%",
            spacing="2",
        ),
        state_class=BaseState
    )