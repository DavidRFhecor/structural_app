import reflex as rx
from structural_app.core.base_state import BaseState

def theory_sidebar():
    return rx.drawer.root(
        rx.drawer.overlay(background_color="rgba(0, 0, 0, 0.3)"),
        rx.drawer.portal(
            rx.drawer.content(
                rx.vstack(
                    # Cabecera
                    rx.hstack(
                        rx.heading("Información Técnica", size="5"),
                        rx.drawer.close(
                            rx.icon_button("x", variant="ghost", on_click=BaseState.toggle_theory)
                        ),
                        justify="between",
                        width="100%",
                    ),
                    
                    # 1. Descripción corta
                    rx.text(
                        BaseState.active_form_config.description, 
                        weight="bold", 
                        size="3"
                    ),
                    
                    rx.divider(),

                    # 2. Información Extendida (Markdown)
                    rx.vstack(
                        rx.heading("Detalles del Cálculo", size="3"),
                        rx.markdown(BaseState.current_theory_content),
                        align_items="start",
                        spacing="2",
                    ),

                    rx.divider(),

                    # 3. Referencias Normativas
                    rx.vstack(
                        rx.heading("Referencias y Normativa", size="3"),
                        rx.foreach(
                            BaseState.active_form_config.references,
                            lambda ref: rx.link(
                                rx.hstack(
                                    rx.icon("book-open", size=16),
                                    rx.text(ref.title, size="2"),
                                    spacing="2",
                                    padding_y="1",
                                ),
                                href=ref.url,
                                is_external=True,
                                color_scheme="blue",
                            )
                        ),
                        align_items="start",
                        spacing="2",
                    ),

                    padding="2em",
                    background_color="white",
                    height="100%",
                    spacing="4",
                    overflow_y="auto", # Permite scroll si hay muchas referencias
                ),
                top="0",
                left="0",
                width="400px",
                height="100vh",
            )
        ),
        direction="left",
        open=BaseState.show_theory_popup,
        on_open_change=BaseState.set_show_theory_popup,
    )