import reflex as rx
from structural_app.shared.components.layout import main_layout
from structural_app.shared.components.result_cards import results_panel
from structural_app.shared.components.status_badges import usage_bar
from structural_app.forms.cortante_circular.state import CortanteCircularState
from structural_app.forms.cortante_circular.sketch import circular_section_svg

def input_panel() -> rx.Component:
    """Panel de parámetros de entrada con validación en tiempo real."""
    return rx.vstack(
        rx.heading("Geometría y Materiales", size="5"),
        rx.divider(),
        rx.grid(
            rx.vstack(
                rx.text("Diámetro (D) [mm]", size="2", weight="medium"),
                rx.input(
                    value=CortanteCircularState.diametro.to(str), 
                    on_change=lambda v: CortanteCircularState.set_value("diametro", v), 
                    type="number",
                    placeholder="Ej: 500"
                ),
                align_items="start"
            ),
            rx.vstack(
                rx.text("fck (Concreto) [MPa]", size="2", weight="medium"),
                rx.input(
                    value=CortanteCircularState.fck.to(str), 
                    on_change=lambda v: CortanteCircularState.set_value("fck", v), 
                    type="number"
                ),
                align_items="start"
            ),
            rx.vstack(
                rx.text("Recubrimiento [mm]", size="2", weight="medium"),
                rx.input(
                    value=CortanteCircularState.recubrimiento.to(str), 
                    on_change=lambda v: CortanteCircularState.set_value("recubrimiento", v), 
                    type="number"
                ),
                align_items="start"
            ),
            columns="2", spacing="3", width="100%"
        ),

        rx.text("Armadura y Cargas", weight="bold", size="3", margin_top="4"),
        rx.divider(),
        rx.grid(
            rx.vstack(
                rx.text("As Principal [mm²]", size="2", weight="medium"),
                rx.input(
                    value=CortanteCircularState.as_principal.to(str), 
                    on_change=lambda v: CortanteCircularState.set_value("as_principal", v), 
                    type="number"
                ),
                align_items="start"
            ),
            rx.vstack(
                rx.text("Ved (Cortante) [kN]", size="2", weight="medium"),
                rx.input(
                    value=CortanteCircularState.ved.to(str), 
                    on_change=lambda v: CortanteCircularState.set_value("ved", v), 
                    type="number"
                ),
                align_items="start"
            ),
            columns="2", spacing="3", width="100%"
        ),

        rx.button(
            "Ejecutar Cálculo", 
            on_click=CortanteCircularState.calculate,
            loading=CortanteCircularState.is_calculating,
            width="100%", 
            color_scheme="blue",
            margin_top="4"
        ),
        spacing="4", 
        width="100%"
    )

def page_content() -> rx.Component:
    """Estructura de la página: 40% entradas, 60% visualización y resultados."""
    return rx.grid(
        # Columna Izquierda: Entradas
        rx.card(
            input_panel(),
            padding="4",
        ),
        
        # Columna Derecha: Visualización y Resultados
        rx.vstack(
            # Card del Croquis SVG
            rx.card(
                rx.vstack(
                    rx.text("Croquis de la Sección", weight="bold", size="3"),
                    rx.center(
                        circular_section_svg(CortanteCircularState),
                        width="100%",
                        padding="1em",
                    ),
                    width="100%",
                ),
                width="100%",
            ),
            
            # Card de Resultados
            rx.cond(
                CortanteCircularState.results.checks.length() > 0,
                rx.card(
                    rx.vstack(
                        results_panel(CortanteCircularState.results),
                        rx.divider(),
                        rx.text("Ratio de Agotamiento", size="2", weight="bold"),
                        usage_bar(
                            CortanteCircularState.results.checks[0].ratio
                        ),
                        width="100%",
                    ),
                    width="100%",
                ),
                # Estado de espera
                rx.card(
                    rx.center(
                        rx.vstack(
                            rx.icon("calculator", size=30, color="gray"),
                            rx.text("Pendiente de cálculo", color="gray", font_style="italic"),
                            spacing="2"
                        ),
                        height="150px",
                        width="100%"
                    ),
                    width="100%"
                )
            ),
            spacing="4",
            width="100%",
        ),
        columns="1", # Por defecto 1 col en móvil
        # En pantallas grandes (md) usamos 2 columnas con proporción 2:3
        grid_template_columns=rx.breakpoints(md="2fr 3fr"),
        spacing="4",
        width="100%",
    )

def cortante_circular_page() -> rx.Component:
    """Función de entrada para el router de Reflex."""
    return main_layout(
        rx.box(
            page_content(),
            on_mount=CortanteCircularState.on_load 
        )
    )