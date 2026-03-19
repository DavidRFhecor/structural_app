import reflex as rx

def form_toolbar(state):
    """Barra de acciones para el formulario activo."""
    return rx.hstack(
        rx.button_group(
            rx.button(
                rx.icon("save"), "Guardar", 
                on_click=state.save_session,
                variant="soft", size="2"
            ),
            rx.upload(
                rx.button(rx.icon("upload"), "Cargar", variant="soft", size="2"),
                id="upload_json",
                on_drop=state.load_session,
                multiple=False,
                accept={
                    "application/json": [".json"]
                },
                max_files=1,
            ),
            variant="ghost",
            is_attached=True,
        ),
        rx.spacer(),
        rx.button(
            rx.icon("refresh-cw"), 
            on_click=state.reset_form,
            variant="ghost", size="2", color_scheme="red"
        ),
        width="100%",
        padding_y="2",
        border_bottom="1px solid #f3f4f6",
    )