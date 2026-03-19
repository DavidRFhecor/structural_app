import reflex as rx

def status_badge(is_ok: bool):
    """Badge de cumplimiento ELU/ELS."""
    return rx.badge(
        rx.cond(is_ok, "CUMPLE", "NO CUMPLE"),
        color_scheme=rx.cond(is_ok, "green", "red"),
        variant="solid",
        size="2"
    )

def usage_bar(ratio: float):
    """Barra de progreso que indica el nivel de agotamiento de la sección."""
    # El color cambia a rojo si supera el 1.0 (100%)
    color = rx.cond(ratio > 1.0, "red", rx.cond(ratio > 0.9, "orange", "green"))
    
    return rx.vstack(
        rx.hstack(
            rx.text("Ratio de utilización", size="1", color_scheme="gray"),
            rx.spacer(),
            rx.text(f"{ratio:.2f}", size="1", weight="bold"),
            width="100%",
        ),
        rx.progress(
            value=ratio * 100,
            color_scheme=color,
            width="100%",
        ),
        spacing="1",
        width="100%",
    )