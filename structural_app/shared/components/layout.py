import reflex as rx
from structural_app.core.base_state import BaseState
from structural_app.core.form_registry import FORM_REGISTRY, discover_forms
from structural_app.shared.components.search_bar import top_search_bar

def navbar(state_class: rx.State = None):
    # Usamos BaseState por defecto si no viene uno específico (para el Portal)
    st = state_class if state_class else BaseState

    # --- DEFINICIÓN DE DIÁLOGOS ---
    dialogs = rx.box(
        # 1. Diálogo de Guardado de Sesión (JSON)
        rx.dialog.root(
            rx.dialog.content(
                rx.dialog.title("Guardar Proyecto"),
                rx.dialog.description("Especifica la ruta y nombre para guardar el archivo de sesión:"),
                rx.vstack(
                    rx.vstack(
                        rx.text("Ruta de la carpeta:", weight="bold", size="2"),
                        rx.input(value=st.save_path, on_change=st.set_save_path, width="100%"),
                        spacing="1", width="100%",
                    ),
                    rx.vstack(
                        rx.text("Nombre del archivo:", weight="bold", size="2"),
                        rx.input(value=st.save_filename, on_change=st.set_save_filename, width="100%"),
                        spacing="1", width="100%",
                    ),
                    spacing="4", margin_y="4", width="100%",
                ),
                rx.flex(
                    rx.button("Cancelar", color_scheme="gray", variant="soft", on_click=st.set_is_save_dialog_open(False)),
                    rx.button("Guardar en Disco", on_click=st.save_session),
                    spacing="3", justify="end",
                ),
            ),
            open=st.is_save_dialog_open,
        ),

        # 2. Diálogo de Exportación de Informe PDF
        rx.dialog.root(
            rx.dialog.content(
                rx.dialog.title("Exportar Informe PDF"),
                rx.dialog.description("El informe profesional se guardará en la ruta del servidor especificada:"),
                rx.vstack(
                    rx.vstack(
                        rx.text("Ruta del servidor:", weight="bold", size="2"),
                        rx.input(value=st.save_path, on_change=st.set_save_path, width="100%"),
                        spacing="1", width="100%",
                    ),
                    rx.vstack(
                        rx.text("Nombre del archivo PDF:", weight="bold", size="2"),
                        rx.input(value=st.pdf_filename, on_change=st.set_pdf_filename, width="100%"),
                        spacing="1", width="100%",
                    ),
                    spacing="4", margin_y="4", width="100%",
                ),
                rx.flex(
                    rx.button("Cancelar", color_scheme="gray", variant="soft", on_click=st.set_is_pdf_dialog_open(False)),
                    rx.button("Generar PDF", on_click=st.export_pdf_to_server),
                    spacing="3", justify="end",
                ),
            ),
            open=st.is_pdf_dialog_open,
        ),

        # 3. NUEVO: Diálogo de Exportación de Excel
        rx.dialog.root(
            rx.dialog.content(
                rx.dialog.title("Exportar a Excel"),
                rx.dialog.description("La hoja de cálculo se guardará en la ruta del servidor especificada:"),
                rx.vstack(
                    rx.vstack(
                        rx.text("Ruta del servidor:", weight="bold", size="2"),
                        rx.input(value=st.save_path, on_change=st.set_save_path, width="100%"),
                        spacing="1", width="100%",
                    ),
                    rx.vstack(
                        rx.text("Nombre del archivo Excel:", weight="bold", size="2"),
                        rx.input(value=st.excel_filename, on_change=st.set_excel_filename, width="100%"),
                        spacing="1", width="100%",
                    ),
                    spacing="4", margin_y="4", width="100%",
                ),
                rx.flex(
                    rx.button("Cancelar", color_scheme="gray", variant="soft", on_click=st.set_is_excel_dialog_open(False)),
                    rx.button("Generar Excel", on_click=st.export_excel_to_server),
                    spacing="3", justify="end",
                ),
            ),
            open=st.is_excel_dialog_open,
        ),

        # 4. Diálogo de Carga 
        rx.dialog.root(
            rx.dialog.content(
                rx.dialog.title("Cargar Proyecto"),
                rx.dialog.description("Arrastra tu archivo JSON aquí:"),
                rx.box(
                    rx.upload(
                        rx.vstack(
                            rx.icon("cloud_upload", size=40, color="gray"),
                            rx.text("Arrastra el archivo .json aquí", weight="bold"),
                            align="center", justify="center", padding="3rem",
                            border="2px dashed #e5e7eb", border_radius="md",
                            width="100%"
                        ),
                        id="navbar_upload",
                        on_drop=st.load_session(rx.upload_files(upload_id="navbar_upload")),
                        multiple=False,
                        accept={"application/json": [".json"]},
                        max_files=1,
                    ),
                    margin_y="4",
                ),
                rx.flex(
                    rx.button("Cancelar", color_scheme="gray", variant="soft", on_click=st.set_is_load_dialog_open(False)),
                    spacing="3", justify="end",
                ),
            ),
            open=st.is_load_dialog_open,
        ),
    )

    # --- LÓGICA DE BOTONES ---
    if state_class:
        action_buttons = rx.hstack(
            rx.button(rx.icon("save"), variant="ghost", on_click=st.set_is_save_dialog_open(True), cursor="pointer"),
            rx.button(rx.icon("upload"), variant="ghost", on_click=st.set_is_load_dialog_open(True), cursor="pointer"),
            
            rx.menu.root(
                rx.menu.trigger(
                    rx.button(
                        rx.icon("download"), 
                        variant="ghost", color_scheme="green", cursor="pointer"
                    ),
                ),
                rx.menu.content(
                    # AHORA ABRE EL DIÁLOGO DE EXCEL
                    rx.menu.item("Exportar a Excel (.xlsx)", on_click=st.open_excel_dialog, cursor="pointer"),
                    rx.menu.separator(),
                    # AHORA ABRE EL DIÁLOGO DEL PDF
                    rx.menu.item("Exportar a PDF Profesional", on_click=st.open_pdf_dialog, cursor="pointer"),
                ),
            ),
            
            rx.button(rx.icon("refresh-cw"), variant="ghost", color_scheme="red", on_click=st.reset_form, cursor="pointer"),
            spacing="3",
        )
    else:
        action_buttons = rx.hstack(
            rx.button(rx.icon("save"), variant="ghost", disabled=True, color_scheme="gray"),
            rx.button(rx.icon("upload"), variant="ghost", on_click=st.set_is_load_dialog_open(True), cursor="pointer"),
            rx.button(rx.icon("download"), variant="ghost", disabled=True, color_scheme="gray"),
            rx.button(rx.icon("refresh-cw"), variant="ghost", disabled=True, color_scheme="gray"),
            spacing="3",
        )

    return rx.hstack(
        dialogs,
        rx.hstack(
            rx.image(
                src="/logo.svg", 
                width="30px", 
                on_click=st.navigate_to_index,
                cursor="pointer"
            ),
            rx.heading(
            "FHECOR | Structural Hub", 
            size="4", 
            color="rgb(0, 50, 100)", # Aplicación directa del color [cite: 129]
            style={"font-weight": "700"}, # Lato Bold para el título
            on_click=st.navigate_to_index,
            cursor="pointer"
            ),
            spacing="3", align="center",
        ),
        rx.spacer(),
        top_search_bar(),
        rx.spacer(),
        action_buttons, 
        align="center", padding="1rem", border_bottom="1px solid #e5e7eb", width="100%",
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
                    on_click=BaseState.navigate_to_form(key), 
                    width="100%",
                    padding="0.5rem",
                    border_radius="md",
                    cursor="pointer",
                    _hover={"bg": "#f3f4f6", "text_decoration": "none"},
                )
                for key, config in FORM_REGISTRY.items()
            ],
            width="100%",
            spacing="1",
        ),
        width="250px", height="100vh", padding="1.5rem", border_right="1px solid #e5e7eb",
    )

def main_layout(content: rx.Component, state_class: rx.State = None):
    return rx.box(
        navbar(state_class), 
        rx.hstack(
            sidebar(),
            rx.box(
                content, flex="1", bg="#f9fafb",
                height="calc(100vh - 64px)", overflow_y="auto", padding="2rem",
            ),
            spacing="0", align_items="flex-start",
        ),
        width="100%",
    )

def version_history_menu(st: any):
    return rx.menu.root(
        rx.menu.trigger(
            rx.button(rx.icon("history"), "Versiones", variant="ghost")
        ),
        rx.menu.content(
            rx.menu.item("v2026-04-14_Final.json", on_click=st.load_specific_version("v2026-04-14_Final.json")),
            rx.menu.item("v2026-04-13_Borrador.json", on_click=st.load_specific_version("v2026-04-13_Borrador.json")),
        )
    )