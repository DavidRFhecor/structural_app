import reflex as rx

from structural_app.core.base_state import BaseState
from structural_app.shared.components.form_renderer import render_dynamic_form
from structural_app.shared.components.result_cards import results_panel
from structural_app.shared.components.sketch_viewer import sketch_viewer


def standard_page_content(config) -> rx.Component:
    return rx.vstack(
        rx.flex(
            rx.box(
                render_dynamic_form(config, BaseState),
                flex="2",
                min_width="0",
                padding="4",
            ),
            rx.box(
                sketch_viewer(BaseState),
                flex="1",
                min_width="320px",
                padding="4",
                border_left={"lg": "1px solid #e5e7eb"},
            ),
            direction={"sm": "column", "lg": "row"},
            width="100%",
            spacing="2",
            align="start",
        ),

        rx.divider(),

        rx.box(
            results_panel(BaseState),
            width="100%",
            padding="4",
        ),

        width="100%",
        spacing="4",
    )