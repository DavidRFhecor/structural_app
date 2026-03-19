import reflex as rx
from ...shared.components.layout import main_layout
from ...shared.components.form_renderer import render_dynamic_form
from ...shared.components.result_cards import results_panel
from ...shared.components.viewer_3d_shell import viewer_3d_shell
from .state import MuroState

def muro_page() -> rx.Component:
    return main_layout(
        rx.grid(
            # Columna Izquierda (40%)
            rx.box(
                render_dynamic_form(MuroState.active_form_config, MuroState),
                width="100%",
            ),
            # Columna Derecha (60%)
            rx.vstack(
                # Visor 3D (Nueva capacidad integrada)
                rx.card(
                    rx.vstack(
                        rx.text("Vista Geométrica 3D", weight="bold"),
                        viewer_3d_shell(MuroState.model_3d_payload),
                    ),
                    width="100%",
                ),
                # Panel de Resultados ELU/ELS
                results_panel(MuroState.results),
                width="100%",
                spacing="4",
            ),
            columns="2",
            spacing="4",
            width="100%",
        )
    )