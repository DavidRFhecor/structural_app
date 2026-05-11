# generic_page_split_tabs.py
import reflex as rx
from ...core.base_state import BaseState
from .form_renderer import _render_element
from .result_cards import results_panel  # ← añadir import


def _tab_nav_bar(config) -> rx.Component:
    return rx.hstack(
        rx.foreach(
            config.tabs,
            lambda tab: rx.button(
                tab.label,
                on_click=BaseState.set_active_tab(tab.id),
                variant=rx.cond(
                    BaseState.left_active_tab == tab.id,
                    "solid",
                    "soft",
                ),
                color_scheme="blue",
                size="2",
                cursor="pointer",
                style={"font_size": "12px"},
            ),
        ),
        spacing="2",
        padding_y="8px",
        width="100%",
        flex_wrap="wrap",
    )


def split_tabs_page_content(config):
    return rx.vstack(
        _tab_nav_bar(config),
        rx.divider(),

        rx.hstack(
            rx.vstack(
                rx.foreach(
                    BaseState.left_column_groups,
                    lambda g: _render_element(g, BaseState),
                ),
                width="50%",
                spacing="4",
                align_items="stretch",
            ),
            rx.vstack(
                rx.foreach(
                    BaseState.right_column_groups,
                    lambda g: _render_element(g, BaseState),
                ),
                width="50%",
                spacing="4",
                align_items="stretch",
            ),
            width="100%",
            padding="4",
            spacing="6",
            align_items="start",
        ),

        # BOTÓN CALCULAR
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
            style={
                "background": "rgb(0,50,100)",
                "color": "white",
                "font_weight": "700",
                "letter_spacing": "0.08em",
                "margin_top": "8px",
                "border_radius": "4px",
                "_hover": {"background": "rgb(0,70,140)"},
            },
        ),

        rx.divider(),  # ← separador antes de resultados

        # PANEL DE RESULTADOS  ← esto faltaba
        rx.box(
            results_panel(BaseState),
            width="100%",
            padding="4",
        ),

        width="100%",
        spacing="4",
    )