import reflex as rx

def custom_data_table(matrix_data: rx.Var, columns: rx.Var, on_edit_fn: any, rows: rx.Var | int):
    return rx.data_editor(
        columns=columns,
        data=matrix_data,
        rows=rows,
        on_cell_edited=on_edit_fn,
        width="100%",
    )