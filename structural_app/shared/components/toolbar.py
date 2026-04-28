import reflex as rx

def form_toolbar(state_class: rx.State, upload_id: str = "upload_json"):
    """Barra de acciones universal con diálogo de guardado."""
    
    # 1. EL DIÁLOGO FLOTANTE DE GUARDADO
    save_dialog = rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Guardar Proyecto en Servidor"),
            rx.dialog.description("Especifica la ruta y el nombre para guardar en la red:"),
            
            rx.vstack(
                rx.vstack(
                    rx.text("Ruta de la carpeta (ej. D:\\Proyectos):", weight="bold", size="2"),
                    rx.input(
                        value=state_class.save_path, 
                        on_change=state_class.set_save_path, 
                        width="100%"
                    ),
                    spacing="1", width="100%",
                ),
                rx.vstack(
                    rx.text("Nombre del archivo:", weight="bold", size="2"),
                    rx.input(
                        value=state_class.save_filename, 
                        on_change=state_class.set_save_filename, 
                        width="100%"
                    ),
                    spacing="1", width="100%",
                ),
                spacing="4", margin_y="4", width="100%",
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
                    "Guardar en Servidor", 
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
        
        rx.hstack(
            # Botón Guardar
            rx.button(
                rx.icon("save"), "Guardar", 
                on_click=state_class.open_save_dialog,
                variant="soft", size="2", cursor="pointer"
            ),
            
            # Botón Cargar
            rx.upload(
                rx.button(rx.icon("upload"), "Cargar", variant="soft", size="2", cursor="pointer"),
                id=upload_id,
                on_drop=state_class.load_session(rx.upload_files(upload_id=upload_id)),
                multiple=False,
                accept={"application/json": [".json"]},
                max_files=1,
            ),
            
            # --- Menú Desplegable de Exportación ---
            rx.menu.root(
                rx.menu.trigger(
                    rx.button(
                        rx.icon("download"), 
                        variant="soft", color_scheme="green", size="2", cursor="pointer"
                    ),
                ),
                rx.menu.content(
                    rx.menu.item(
                        "Exportar a Excel (.xlsx)", 
                        on_click=state_class.export_excel,
                        cursor="pointer"
                    ),
                    rx.menu.separator(),
                    rx.menu.item(
                        "Exportar a PDF", 
                        on_click=state_class.export_pdf,
                        cursor="pointer"
                    ),
                ),
            ),
            spacing="1", 
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