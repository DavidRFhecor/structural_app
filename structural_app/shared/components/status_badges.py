import reflex as rx

def status_badge(is_ok: bool):
    """Badge de cumplimiento ELU/ELS."""
    return rx.badge(
        rx.cond(is_ok, "CUMPLE", "NO CUMPLE"),
        color_scheme=rx.cond(is_ok, "green", "red"),
        variant="solid",
        size="2"
    )

def usage_bar(ratio: rx.Var): # Asegúrate de que reciba el Var
    # Convertimos el resultado de la operación a entero
    progress_value = (ratio * 100).to(int) 
    
    color = rx.cond(ratio > 1.0, "red", rx.cond(ratio > 0.9, "orange", "green"))
    
    return rx.vstack(
        # ... tu código anterior de los textos ...
        rx.progress(
            value=progress_value, # Ahora es un int garantizado
            color_scheme=color,
            width="100%",
        ),
        spacing="1",
        width="100%",
    )