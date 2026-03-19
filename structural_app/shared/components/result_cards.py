import reflex as rx

def check_card(check: rx.Var):
    """Renderiza una tarjeta individual de comprobación normativa."""
    return rx.card(
        rx.hstack(
            rx.vstack(
                rx.text(check.description, weight="bold"),
                rx.text(f"Valor: {check.value} / Límite: {check.limit}", size="2"),
                align_items="start",
            ),
            rx.spacer(),
            # Badge dinámico según el ratio
            rx.badge(
                rx.cond(check.status, "CUMPLE", "NO CUMPLE"),
                color_scheme=rx.cond(check.status, "green", "red"),
                variant="surface",
            ),
            width="100%",
            align_items="center",
        ),
        margin_bottom="2",
    )

def results_panel(response: rx.Var):
    """Panel derecho que muestra el resumen y la lista de comprobaciones."""
    return rx.vstack(
        rx.heading("Resultados del Cálculo", size="5"),
        rx.text(response.summary, color_scheme="gray"),
        rx.divider(),
        
        # CAMBIO CRÍTICO: Usamos rx.foreach en lugar de list comprehension
        rx.foreach(
            response.checks,
            lambda c: check_card(c)
        ),
        
        width="100%",
        spacing="4",
        padding="4",
    )