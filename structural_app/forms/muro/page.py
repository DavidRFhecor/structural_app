import reflex as rx
from structural_app.shared.components.layout import main_layout
from structural_app.shared.components.result_cards import results_panel
from structural_app.shared.components.status_badges import usage_bar
from structural_app.forms.muro.state import MuroState
from structural_app.shared.components.muro_3d import muro_visualizer

def muro_input_panel() -> rx.Component:
    """Panel de entradas específico para muros de contención."""
    return rx.vstack(
        rx.heading("Geometría del Muro (m)", size="5"),
        rx.divider(),
        rx.grid(
            rx.vstack(
                rx.text("Altura Fuste (h)", size="2", weight="medium"),
                rx.input(
                    value=MuroState.h_muro.to(str), 
                    on_change=lambda v: MuroState.set_value("h_muro", v), 
                    type="number"
                ),
            ),
            rx.vstack(
                rx.text("Espesor Base (e)", size="2", weight="medium"),
                rx.input(
                    value=MuroState.e_inferior.to(str), 
                    on_change=lambda v: MuroState.set_value("e_inferior", v), 
                    type="number"
                ),
            ),
            rx.vstack(
                rx.text("Ancho Zapata (b)", size="2", weight="medium"),
                rx.input(
                    value=MuroState.b_zapata.to(str), 
                    on_change=lambda v: MuroState.set_value("b_zapata", v), 
                    type="number"
                ),
            ),
            rx.vstack(
                rx.text("Vuelo Puntera (c)", size="2", weight="medium"),
                rx.input(
                    value=MuroState.c_puntera.to(str), 
                    on_change=lambda v: MuroState.set_value("c_puntera", v), 
                    type="number"
                ),
            ),
            columns="2", spacing="3", width="100%"
        ),

        rx.text("Materiales", weight="bold", size="3", margin_top="4"),
        rx.divider(),
        rx.grid(
            rx.vstack(
                rx.text("fck (Concreto) [MPa]", size="2"),
                rx.input(value=MuroState.fck.to(str), on_change=lambda v: MuroState.set_value("fck", v), type="number"),
            ),
            rx.vstack(
                rx.text("fyk (Acero) [MPa]", size="2"),
                rx.input(value=MuroState.fyk.to(str), on_change=lambda v: MuroState.set_value("fyk", v), type="number"),
            ),
            columns="2", spacing="3", width="100%"
        ),

        rx.button(
            "Calcular Armado y Estabilidad", 
            on_click=MuroState.calculate,
            loading=MuroState.is_calculating,
            width="100%", 
            color_scheme="green",
            margin_top="4"
        ),
        spacing="4", width="100%"
    )

def muro_page_content() -> rx.Component:
    return rx.grid(
        # Columna Izquierda: Entradas
        rx.card(muro_input_panel(), padding="4"),
        
        # Columna Derecha: 3D y Resultados
        rx.vstack(
            rx.card(
                rx.vstack(
                    rx.text("Vista Muro 3D", weight="bold", size="3"),
                    # Pasamos directamente la variable de la figura del State
                    muro_visualizer(MuroState.muro_figure), 
                    width="100%",
                ),
                width="100%",
            ), # <--- AQUÍ ESTABA LA COMA QUE FALTABA
            
            rx.cond(
                MuroState.results.checks.length() > 0,
                rx.card(
                    rx.vstack(
                        results_panel(MuroState.results),
                        rx.divider(),
                        usage_bar(MuroState.results.checks[0].ratio),
                        width="100%",
                    ),
                    width="100%",
                ),
                rx.card(
                    rx.center(rx.text("Configure la geometría y pulse calcular", color="gray"), height="150px"),
                    width="100%"
                )
            ),
            spacing="4", width="100%",
        ),
        grid_template_columns=rx.breakpoints(md="2fr 3fr"),
        spacing="4", width="100%",
    )

def muro_page() -> rx.Component:
    """Esta es la función que registra el formulario 'muro'."""
    return main_layout(
        rx.box(
            muro_page_content(),
            on_mount=MuroState.on_load 
        )
    )