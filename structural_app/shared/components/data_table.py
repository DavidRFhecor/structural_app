import reflex as rx
from structural_app.core.base_state import BaseState

HEADER_STYLE = {
    "background": "rgb(0, 50, 100)",
    "color": "white",
    "padding": "4px 8px",
    "font_size": "11px",
    "font_weight": "600",
    "text_align": "center",
    "border": "1px solid rgb(0, 40, 80)",
    "min_width": "80px",
}

CELL_STYLE = {
    "padding": "2px",
    "border": "1px solid var(--gray-4)",
    "min_width": "80px",
}

INPUT_STYLE = {
    "width": "100%",
    "font_size": "12px",
    "font_family": "'Courier New', monospace",
    "text_align": "right",
    "border": "none",
    "background": "transparent",
    "padding": "2px 4px",
}


def _cell(table_id: str, row_idx: int, col_idx: int, value: rx.Var) -> rx.Component:
    return rx.td(
        rx.input(
            value=value.to(str),
            on_change=lambda v: BaseState.update_table_cell(
                table_id, (row_idx, col_idx), v
            ),
            style=INPUT_STYLE,
        ),
        style=CELL_STYLE,
    )


def custom_data_table(
    table_id: str,
    col_headers: list[str],
) -> rx.Component:
    """
    Tabla editable genérica.
    - table_id: clave en BaseState.table_data
    - col_headers: lista de strings con los títulos de columna
    """
    matrix = BaseState.table_data[table_id]

    header_cells = [rx.table.column_header_cell(h, style=HEADER_STYLE) for h in col_headers]

    return rx.vstack(
        rx.table.root(
            rx.table.header(
                rx.table.row(*header_cells),
            ),
            rx.table.body(
                rx.foreach(
                    matrix,
                    lambda row, row_idx: rx.table.row(
                        rx.foreach(
                            row,
                            lambda cell, col_idx: rx.table.cell(
                                rx.input(
                                    value=cell.to(str),
                                    on_change=lambda v: BaseState.update_table_cell(
                                        table_id, (row_idx, col_idx), v
                                    ),
                                    style=INPUT_STYLE,
                                    variant="surface",
                                    size="1",
                                ),
                                style=CELL_STYLE,
                            ),
                        ),
                    ),
                ),
            ),
            variant="surface",
            width="100%",
        ),
        rx.hstack(
            rx.button(
                rx.icon("plus", size=14), "Añadir fila",
                on_click=BaseState.add_table_row(table_id),
                size="1", variant="soft", color_scheme="blue",
            ),
            rx.button(
                rx.icon("minus", size=14), "Eliminar última",
                on_click=BaseState.remove_table_row(table_id),
                size="1", variant="soft", color_scheme="red",
            ),
            spacing="2", justify="end", width="100%", padding_top="1",
        ),
        width="100%",
        spacing="1",
    )