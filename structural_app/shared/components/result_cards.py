import reflex as rx

def check_card(check: any):
    """Renderiza una tarjeta individual para cada comprobación (VRdc, wk, etc.)"""
    return rx.card(
        rx.hstack(
            rx.vstack(
                rx.text(check.description, size="2", weight="bold"),
                rx.hstack(
                    rx.text(f"{check.value} {check.unit}", size="4", weight="bold"),
                    rx.text(f" / Límite: {check.limit}", size="2", color_scheme="gray"),
                    align="baseline",
                ),
                align_items="start",
                spacing="1",
            ),
            rx.spacer(),
            # Badge de estado: Verde si cumple, Rojo si no
            rx.badge(
                rx.cond(check.status, "CUMPLE", "NO CUMPLE"),
                color_scheme=rx.cond(check.status, "green", "red"),
                variant="solid",
                size="2",
            ),
            width="100%",
            align="center",
        ),
        width="100%",
        variant="surface",
    )

def results_panel(state: any):
    """Panel principal de resultados con checks y gráficos."""
    res = state.results

    return rx.vstack(
       rx.heading(
            "Resultados del Cálculo", 
            size="6", 
            color="rgb(0, 50, 100)", # Color corporativo 
            mb="2"
        ),
        
        rx.cond(
            res,
            rx.vstack(
                # 1. Resumen de texto
                rx.callout(
                    res.summary,
                    icon="info",
                    color_scheme=rx.cond(res.is_ok, "blue", "red"),
                    width="100%",
                ),

                # 2. Lista de Comprobaciones (Checks)
                rx.text("Comprobaciones Normativas", size="3", weight="bold", mt="4"),
                rx.vstack(
                    rx.foreach(
                        res.checks,
                        lambda c: check_card(c)
                    ),
                    width="100%",
                    spacing="2",
                ),

                # 3. Gráficos Interactivos (Plotly)
                rx.cond(
                    res.plot_data,
                    rx.vstack(
                        rx.text("Visualización y Diagramas", size="3", weight="bold", mt="6"),
                        rx.plotly(
                            data=res.plot_data,
                            width="100%",
                            height="400px",
                        ),
                        width="100%",
                    )
                ),
                width="100%",
                align_items="start",
            ),
            # Mensaje cuando no hay resultados
            rx.center(
                rx.vstack(
                    rx.icon("calculator", size=40, color="var(--gray-8)"),
                    rx.text("Introduce los datos y pulsa 'Calcular'.", color_scheme="gray"),
                    align="center",
                    padding="10",
                    border="2px dashed var(--gray-4)",
                    border_radius="xl",
                    width="100%",
                ),
                width="100%",
            )
        ),
        width="100%",
        spacing="4",
    )