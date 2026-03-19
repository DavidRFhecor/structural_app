import reflex as rx
from ....shared.components.layout import main_layout
from ....shared.components.form_renderer import render_dynamic_form
from ....shared.components.result_cards import results_panel
from .state import ElementState

def page_content() -> rx.Component:
    return rx.grid(
        # Panel de Entradas (40%)
        rx.box(
            render_dynamic_form(ElementState.active_form_config, ElementState),
            width="100%",
        ),
        # Panel de Resultados (60%)
        rx.box(
            rx.cond(
                ElementState.results,
                results_panel(ElementState.results),
                rx.center(rx.text("Introduzca datos y pulse calcular", color="gray"))
            ),
            width="100%",
        ),
        columns="2",
        spacing="4",
    )

def template_page() -> rx.Component:
    return main_layout(page_content())