import reflex as rx

def circular_section_svg(state: any):
    """Genera el contenedor para el SVG reactivo."""
    return rx.center(
        # Usamos rx.html para inyectar el texto SVG que creamos en el State
        rx.html(state.svg_string),
        width="100%",
        padding="2",
        bg="white",
        border_radius="md",
        border="1px solid #f3f4f6"
    )