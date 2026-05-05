# En structural_app/shared/components/theory_sidebar.py
import reflex as rx
from structural_app.core.base_state import BaseState

def theory_sidebar(config: rx.Var):
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.heading("Información Técnica", size="5"),
                rx.spacer(),
                rx.icon("x", cursor="pointer", on_click=BaseState.toggle_theory),
                width="100%",
                align="center",
            ),
            rx.text(config["extended_info"], size="2"),
            rx.divider(),
            rx.text("Referencias y Libros:", weight="bold", size="2"),
            rx.foreach(
                config["references"],
                lambda ref: rx.link(
                    rx.hstack(rx.icon("book-text", size=16), rx.text(ref["title"], size="2")),
                    href=ref["url"],
                    is_external=True,
                )
            ),
            spacing="4",
            padding="6",
        ),
        position="fixed",
        left=rx.cond(BaseState.show_theory_sidebar, "0", "-400px"),
        top="0",
        width="350px",
        height="100vh",
        background_color=rx.color("gray", 2),
        box_shadow="5px 0px 15px rgba(0,0,0,0.1)",
        z_index="1000",
        transition="left 0.3s ease-in-out",
    )