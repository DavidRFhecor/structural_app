import reflex as rx
from structural_app.core.form_registry import FORM_REGISTRY, discover_forms
from structural_app.shared.components.search_bar import top_search_bar

# 1. NAVBAR RECIBE EL ESTADO
def navbar(state_class: rx.State = None):
    
    if state_class:
        action_buttons = rx.hstack(
            # 1. DIÁLOGO DE GUARDADO
            rx.dialog.root(
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
                        rx.button("Cancelar", color_scheme="gray", variant="soft", on_click=state_class.set_is_save_dialog_open(False), cursor="pointer"),
                        rx.button("Confirmar Guardado", on_click=state_class.save_session, cursor="pointer"),
                        spacing="3",
                        justify="end",
                    ),
                ),
                open=state_class.is_save_dialog_open,
            ),
            
            # 2. NUEVO POP-UP DE CARGA
            # 1. DIÁLOGO DE GUARDADO CON RUTA EN EL SERVIDOR
            rx.dialog.root(
                rx.dialog.content(
                    rx.dialog.title("Guardar Proyecto"),
                    rx.dialog.description("Especifica dónde quieres guardar el archivo físico:"),
                    
                    rx.vstack(
                        rx.vstack(
                            rx.text("Ruta de la carpeta (Absoluta o relativa):", weight="bold", size="2"),
                            rx.input(
                                value=state_class.save_path,
                                on_change=state_class.set_save_path,
                                placeholder="Ej: D:\\Proyectos\\FHECOR\\",
                                width="100%",
                            ),
                            spacing="1", # Muy pegadito al input
                            width="100%",
                        ),
                        
                        # --- GRUPO 2: LABEL + INPUT PARA EL NOMBRE ---
                        rx.vstack(
                            rx.text("Nombre del archivo:", weight="bold", size="2"),
                            rx.input(
                                value=state_class.save_filename,
                                on_change=state_class.set_save_filename,
                                placeholder="diseño_muro.json",
                                width="100%",
                            ),
                            spacing="1", # Muy pegadito al input
                            width="100%",
                        ),
                        
                        spacing="4", # Separación mayor entre los dos bloques
                        margin_y="4",
                        width="100%",
                    ),
                    
                    rx.flex(
                        rx.button("Cancelar", color_scheme="gray", variant="soft", on_click=state_class.set_is_save_dialog_open(False), cursor="pointer"),
                        rx.button("Guardar en Disco", on_click=state_class.save_session, cursor="pointer"),
                        spacing="3",
                        justify="end",
                    ),
                ),
                open=state_class.is_save_dialog_open,
            ),
            
            # 3. LOS BOTONES VISIBLES EN LA BARRA SUPERIOR
            rx.button(rx.icon("save"), variant="ghost", on_click=state_class.open_save_dialog, cursor="pointer", title="Guardar proyecto"),
            # El botón de subir ahora solo abre el pop-up
            rx.button(rx.icon("upload"), variant="ghost", on_click=state_class.set_is_load_dialog_open(True), cursor="pointer", title="Cargar proyecto"),
            rx.button(rx.icon("refresh-cw"), variant="ghost", color_scheme="red", on_click=state_class.reset_form, cursor="pointer", title="Limpiar datos"),
            spacing="3",
        )
    else:
        # Estado inactivo para el inicio
        action_buttons = rx.hstack(
            rx.button(rx.icon("save"), variant="ghost", disabled=True),
            rx.button(rx.icon("upload"), variant="ghost", disabled=True),
            spacing="3",
        )

    return rx.hstack(
        rx.hstack(
            rx.image(src="/logo.svg", width="30px"),
            rx.heading("FHECOR | Structural Design Hub", size="4"),
            spacing="3",
            align="center",
        ),
        rx.spacer(),
        top_search_bar(),
        rx.spacer(),
        action_buttons, 
        align="center",
        padding="1rem",
        border_bottom="1px solid #e5e7eb",
        width="100%",
    )

def sidebar():
    return rx.vstack(
        rx.text("CALCULADORAS", weight="bold", size="1", color_scheme="gray", margin_bottom="1rem"),
        rx.vstack(
            *[
                rx.link(
                    rx.hstack(
                        rx.icon("calculator", size=16),
                        rx.text(config["title"], size="2"),
                    ),
                    href=f"/{key.replace('_', '-')}",
                    width="100%",
                    padding="0.5rem",
                    border_radius="md",
                    _hover={"bg": "#f3f4f6", "text_decoration": "none"},
                )
                for key, config in FORM_REGISTRY.items()
            ],
            width="100%",
            spacing="1",
        ),
        width="250px",
        height="100vh",
        padding="1.5rem",
        border_right="1px solid #e5e7eb",
    )

# 2. MAIN LAYOUT AHORA RECIBE EL ESTADO Y SE LO PASA A LA NAVBAR
def main_layout(content: rx.Component, state_class: rx.State = None):
    return rx.box(
        navbar(state_class), # Le pasamos el estado a la barra superior
        rx.hstack(
            sidebar(),
            rx.box(
                content,
                flex="1",
                bg="#f9fafb",
                height="calc(100vh - 64px)",
                overflow_y="auto",
                padding="2rem",
            ),
            spacing="0",
            align_items="flex-start",
        ),
        width="100%",
    )

FormRegistry = discover_forms()
FORM_REGISTRY = FormRegistry