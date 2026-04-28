import reflex as rx
from structural_app.core.base_state import BaseState
from structural_app.shared.components.layout import main_layout
from structural_app.core.form_registry import FORM_REGISTRY

def index() -> rx.Component:
    return main_layout(
        rx.vstack(
            rx.heading("Dashboard de Cálculo Estructural", size="8", margin_bottom="1rem"),
            rx.text("Acceda a los módulos normativos basados en el motor FHECOR Structural Codes.", color_scheme="gray"),
                        
            rx.grid(
                *[
                    # Convertimos la tarjeta en el propio botón
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.badge(config.get("category", "General"), color_scheme="blue"),
                                rx.spacer(),
                                rx.icon("chevron-right", color="gray"),
                                width="100%",
                            ),
                            rx.heading(config["title"], size="4"),
                            rx.text(config.get("description", "Sin descripción disponible."), size="2", line_limit=2, color_scheme="gray"),
                            spacing="3",
                            width="100%",
                        ),
                        # --- LÓGICA DE CLIC EN TODA LA TARJETA ---
                        on_click=BaseState.navigate_to_form(key),
                        style={
                            "cursor": "pointer",
                            "_hover": {
                                "border_color": "var(--blue-8)",
                                "box_shadow": "0 4px 12px rgba(0, 0, 0, 0.1)",
                                "transform": "translateY(-2px)",
                            },
                            "transition": "all 0.2s ease-in-out",
                        },
                        height="180px", 
                        padding="4",
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