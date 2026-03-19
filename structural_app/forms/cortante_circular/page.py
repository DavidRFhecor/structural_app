import reflex as rx
from structural_app.shared.components.layout import main_layout
from structural_app.shared.components.form_renderer import render_dynamic_form
from structural_app.shared.components.result_cards import results_panel
from structural_app.shared.components.status_badges import usage_bar
from .state import CortanteCircularState
from .sketch import circular_section_svg

def page_content() -> rx.Component:
    """Define la estructura interna de la página de cortante circular."""
    return rx.grid(
        # Columna Izquierda: Formulario de Entradas (40%)
        rx.card(
            rx.vstack(
                render_dynamic_form(CortanteCircularState.active_form_config, CortanteCircularState),
                spacing="4",
            ),
            padding="4",
        ),
        
        # Columna Derecha: Visualización y Resultados (60%)
        rx.vstack(
            # Card de Visualización Geométrica (SVG)
            rx.card(
                rx.vstack(
                    rx.text("Croquis de la Sección", weight="bold", size="3"),
                    circular_section_svg(CortanteCircularState),
                    width="100%",
                ),
                width="100%",
            ),
            
            # Card de Resultados y Ratios
            rx.cond(
                CortanteCircularState.results,
                rx.card(
                    rx.vstack(
                        results_panel(CortanteCircularState.results),
                        rx.divider(),
                        # Mostramos el ratio principal de forma destacada
                        usage_bar(
                            rx.cond(
                                CortanteCircularState.results.checks.length() > 0,
                                CortanteCircularState.results.checks[0].ratio,
                                0.0
                            )
                        ),
                        width="100%",
                    ),
                    width="100%",
                ),
                rx.center(
                    rx.text("Introduzca datos y pulse 'Calcular' para ver los resultados", color="gray", font_style="italic"),
                    height="200px", width="100%"
                )
            ),
            spacing="4",
            width="100%",
        ),
        columns="2",
        spacing="4",
        width="100%",
    )

def cortante_circular_page() -> rx.Component:
    """Punto de entrada de la página con el evento de carga crucial."""
    return main_layout(
        rx.box(
            page_content(),
            # ESTA LÍNEA ES LA QUE SOLUCIONA TU PROBLEMA:
            # Fuerza al estado a identificarse como 'cortante_circular' al entrar
            on_mount=CortanteCircularState.on_load 
        )
    )