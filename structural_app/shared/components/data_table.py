import reflex as rx

def custom_data_table(matrix_data: rx.Var, columns: list[dict], on_edit_fn: any):
    return rx.data_editor(
        columns=columns,
        data=matrix_data,
        on_cell_edited=on_edit_fn, # Pasamos la referencia directa a la función corregida
        width="100%",
    )