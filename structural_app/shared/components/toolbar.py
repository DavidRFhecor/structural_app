import reflex as rx

def form_toolbar(state_class: rx.State, upload_id: str = "upload_json"):
    """Barra de acciones universal con diálogo de guardado."""
    
    # 1. EL DIÁLOGO FLOTANTE DE GUARDADO
    save_dialog = rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Guardar Proyecto"),
            rx.dialog.description("Introduce el nombre con el que deseas guardar este cálculo:"),
            
            rx.box(
                rx.input(
                    value=state_class.save_filename,
                    on_change=state_class.set_save_filename, 
                    placeholder="nombre_del_archivo.json",
                ),
                margin_y="4",
            ),
            
            rx.flex(
                rx.button(
                    "Cancelar", 
                    color_scheme="gray", 
                    variant="soft", 
                    on_click=state_class.set_is_save_dialog_open(False),
                    cursor="pointer",
                ),
                rx.button(
                    "Confirmar Guardado", 
                    on_click=state_class.save_session, 
                    cursor="pointer",
                ),
                spacing="3",
                justify="end",
            ),
        ),
        open=state_class.is_save_dialog_open,
    )

    # 2. LA BARRA DE HERRAMIENTAS PRINCIPAL
    return rx.hstack(
        save_dialog,
        
        # SUSTITUIMOS BUTTON_GROUP POR HSTACK
        rx.hstack(
            rx.button(
                rx.icon("save"), "Guardar", 
                on_click=state_class.open_save_dialog,
                variant="soft", size="2", cursor="pointer"
            ),
            rx.upload(
                rx.button(rx.icon("upload"), "Cargar", variant="soft", size="2", cursor="pointer"),
                id=upload_id,
                on_drop=state_class.load_session(rx.upload_files(upload_id=upload_id)),
                multiple=False,
                accept={"application/json": [".json"]},
                max_files=1,
            ),
            spacing="1", # Espacio pequeño para que parezcan agrupados
        ),
        
        rx.spacer(),
        rx.button(
            rx.icon("refresh-cw"), 
            on_click=state_class.reset_form,
            variant="ghost", size="2", color_scheme="red", cursor="pointer"
        ),
        width="100%",
        padding_y="2",
        border_bottom="1px solid #f3f4f6",
    )