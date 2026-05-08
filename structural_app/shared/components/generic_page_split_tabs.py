import reflex as rx

from structural_app.core.base_state import BaseState
from structural_app.shared.components.form_renderer import (
    render_form_header,
    render_tab_content,
)
from structural_app.shared.components.result_cards import results_panel


def _tab_panel(
    config,
    active_tab,
    disabled_tab,
    on_change,
) -> rx.Component:
    return rx.card(
        rx.tabs.root(
            rx.tabs.list(
                rx.foreach(
                    config.tabs,
                    lambda tab: rx.tabs.trigger(
                        tab.label,
                        value=tab.id,
                        disabled=tab.id == disabled_tab,
                        style={
                            "font_size": "12px",
                            "padding": "6px 12px",
                        },
                    ),
                ),
                style={
                    "border_bottom": "2px solid rgb(0,50,100)",
                    "width": "100%",
                },
            ),
            rx.foreach(
                config.tabs,
                lambda tab: rx.tabs.content(
                    render_tab_content(tab, BaseState),
                    value=tab.id,
                ),
            ),
            value=active_tab,
            on_change=on_change,
            width="100%",
        ),
        width="100%",
        padding="3",
    )


def split_tabs_page_content(config) -> rx.Component:
    return rx.vstack(
        render_form_header(config),

        rx.grid(
            _tab_panel(
                config=config,
                active_tab=BaseState.left_active_tab,
                disabled_tab=BaseState.right_active_tab,
                on_change=BaseState.set_left_active_tab,
            ),
            _tab_panel(
                config=config,
                active_tab=BaseState.right_active_tab,
                disabled_tab=BaseState.left_active_tab,
                on_change=BaseState.set_right_active_tab,
            ),
            columns={
                "initial": "1",
                "lg": "2",
            },
            spacing="4",
            width="100%",
            align_items="start",
        ),

        rx.button(
            rx.hstack(
                rx.icon("calculator", size=16),
                rx.text("CALCULAR"),
                spacing="2",
                align="center",
            ),
            on_click=BaseState.calculate,
            loading=BaseState.is_calculating,
            width="100%",
            size="2",
            color_scheme="blue",
            margin_top="4",
        ),

        rx.divider(),

        rx.box(
            results_panel(BaseState),
            width="100%",
        ),

        width="100%",
        spacing="4",
        padding="4",
    )