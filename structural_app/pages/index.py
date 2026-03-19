import reflex as rx
from structural_app.shared.components.layout import main_layout
from ..core.form_registry import FORM_REGISTRY

def index() -> rx.Component:
    return main_layout(
        rx.vstack(
            rx.heading("Dashboard de Cálculo Estructural", size="8", margin_bottom="1rem"),
            rx.text("Acceda a los módulos normativos basados en el motor FHECOR Structural Codes.", color_scheme="gray"),
                        
            rx.grid(
                *[
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.badge(config.get("category", "General"), color_scheme="blue"),
                                rx.spacer(),
                                rx.icon("chevron-right", color="gray"),
                                width="100%",
                            ),
                            rx.heading(config["title"], size="4"),
                            rx.text(config["description"], size="2", line_limit=2),
                            rx.button(
                                "Abrir Calculadora", 
                                variant="soft", 
                                width="100%",
                                on_click=rx.redirect(f"/{key.replace('_', '-')}")
                            ),
                            spacing="3",
                        ),
                        height="220px",
                    )
                    for key, config in FORM_REGISTRY.items()
                ],
                columns="3",
                spacing="4",
                width="100%",
            ),
            width="100%",
            spacing="4",
        )
    )