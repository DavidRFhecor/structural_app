# generic_page_split_tabs.py
import reflex as rx
from ...core.base_state import BaseState
from .form_renderer import _render_element
from .result_cards import results_panel


# ---------------------------------------------------------------------------
# Barra superior de TABS (1. Geometría / 2. Relleno / etc.)
# ---------------------------------------------------------------------------
def _tab_nav_bar(config) -> rx.Component:
    return rx.hstack(
        rx.foreach(
            config.tabs,
            lambda tab: rx.button(
                tab.label,
                on_click=BaseState.set_active_tab(tab.id),
                variant=rx.cond(
                    BaseState.active_tab == tab.id,
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


# ---------------------------------------------------------------------------
# Barra de GRUPOS del tab activo (dentro de cada columna)
# Muestra todos los grupos del tab; al pulsar uno lo activa en su columna.
# ---------------------------------------------------------------------------
def _group_nav_bar() -> rx.Component:
    return rx.hstack(
        rx.foreach(
            BaseState.toolbar_groups,
            lambda group: rx.button(
                group.name,
                on_click=BaseState.set_active_group(group.column, group.id),
                variant=rx.cond(
                    BaseState.active_group_per_column.get(
                        "col_" + group.column.to_string()
                    ) == group.id,
                    "solid",
                    "outline",
                ),
                color_scheme="gray",
                size="1",
                cursor="pointer",
                style={"font_size": "11px"},
            ),
        ),
        spacing="1",
        padding_y="4px",
        width="100%",
        flex_wrap="wrap",
        border_bottom="1px solid #e5e7eb",
        padding_bottom="6px",
    )


# ---------------------------------------------------------------------------
# Columna individual — renderiza el grupo visible de esa columna
# ---------------------------------------------------------------------------
def _column(col_groups: list[rx.Var], width: str) -> rx.Component:
    return rx.vstack(
        rx.foreach(
            col_groups,
            lambda g: _render_element(g, BaseState),
        ),
        width=width,
        spacing="4",
        align_items="stretch",
        min_width="0",
    )


# ---------------------------------------------------------------------------
# Layout principal
# ---------------------------------------------------------------------------
def split_tabs_page_content(config) -> rx.Component:
    return rx.vstack(
        # Barra de tabs (1. Geometría, 2. Relleno…)
        _tab_nav_bar(config),

        # Columnas de contenido — 2 columnas (extensible a 3 con num_columns=3)
        rx.hstack(
            rx.foreach(
                BaseState.columns_groups,
                lambda col_groups: rx.vstack(
                    rx.foreach(
                        col_groups,
                        lambda g: _render_element(g, BaseState),
                    ),
                    width=f"100%",
                    spacing="4",
                    align_items="stretch",
                    min_width="0",
                    flex="1",
                ),
            ),
            width="100%",
            padding_x="4",
            spacing="6",
            align_items="start",
        ),

        # Botón CALCULAR
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

        rx.divider(),

        # Panel de resultados
        rx.box(
            results_panel(BaseState),
            width="100%",
            padding="4",
        ),

        width="100%",
        spacing="0",
        padding="4",
    )