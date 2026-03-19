import reflex as rx
from ...shared.components.layout import main_layout
from ...shared.components.form_renderer import render_dynamic_form
from ...shared.components.result_cards import results_panel
from .state import CortanteCircularState
from .sketch import circular_section_svg

def cortante_circular_page() -> rx.Component:
    return main_layout(
        rx.grid(
            # Panel Izquierdo: Inputs del Excel
            rx.box(
                render_dynamic_form(
                    CortanteCircularState.active_form_config, 
                    CortanteCircularState
                ),
                width="100%",
            ),
            # Panel Derecho: Visualización Técnica + Resultados
            rx.vstack(
                # El Croquis Reactivo
                rx.card(
                    rx.vstack(
                        rx.text("Esquema de la Sección", size="2", weight="bold"),
                        circular_section_svg(CortanteCircularState),
                    ),
                    width="100%",
                ),
                # Las tarjetas de cumplimiento normativo
                results_panel(CortanteCircularState.results),
                width="100%",
                spacing="4",
            ),
            columns="2",
            spacing="4",
            width="100%",
        )
    )