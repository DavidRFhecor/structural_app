import reflex as rx
from structural_app.core.form_registry import FORM_REGISTRY, discover_forms
from structural_app.shared.components.search_bar import top_search_bar

def navbar():
    return rx.hstack( # Cambiamos flex por hstack para alinear verticalmente todo al centro
        # Logo y Título
        rx.hstack(
            rx.image(src="/logo.svg", width="30px"),
            rx.heading("FHECOR | Structural Design Hub", size="4"),
            spacing="3",
            align="center",
        ),
        
        rx.spacer(),
        
        # Buscador Integrado
        top_search_bar(),
        
        rx.spacer(), # Añadimos otro spacer para que el buscador quede centrado en la pantalla
        
        # Botones de acción guardar y cargar
        rx.hstack(
            rx.button(rx.icon("save"), variant="ghost"),
            rx.button(rx.icon("file-down"), variant="ghost"),
            spacing="3",
        ),
        align="center", # Alineación vertical cruzada
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

def main_layout(content: rx.Component):
    return rx.box(
        navbar(),
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