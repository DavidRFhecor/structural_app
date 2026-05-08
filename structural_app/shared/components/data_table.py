import reflex as rx
from typing import Any

from structural_app.core.base_state import BaseState


def custom_data_table(
    matrix_data: Any,
    columns: Any,
    rows: Any,
    table_id: str,
):
    return rx.data_editor(
        columns=columns,
        data=matrix_data,
        rows=rows,
        on_cell_edited=lambda pos, value: BaseState.update_table_cell(
            table_id,
            pos,
            value,
        ),
        width="100%",
    )