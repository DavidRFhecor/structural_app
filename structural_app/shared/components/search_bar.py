import reflex as rx
from structural_app.core.base_state import BaseState, SearchResult

def render_search_result(result: SearchResult):
    """Diseño de cada tarjeta de resultado en la lista."""
    return rx.box(
        rx.vstack(
            rx.text(result.title, weight="bold", size="2"),
            rx.text(result.description, size="1", color_scheme="gray"),
            align_items="start",
            spacing="1",
        ),
        padding="2",
        width="100%",
        border_radius="md",
        # Efecto hover para que parezca un botón interactivo
        _hover={"bg": rx.color("accent", 3), "cursor": "pointer"},
        # Al hacer clic, navega y limpia el buscador
        on_click=[
            BaseState.navigate_to_form(result.form_key),
            BaseState.clear_search
        ]
    )

def top_search_bar():
    """Componente principal del buscador con menú desplegable."""
    return rx.box(
        # Barra de entrada de texto
        rx.input(
            placeholder="Buscar cálculo (ej. Viga, Cortante...)",
            value=BaseState.search_query,
            # Reflex crea automáticamente set_search_query para actualizar el State
            on_change=BaseState.set_search_query,
            radius="full",
            width="300px",
            background_color="white",
        ),
        
        # Caja de resultados flotante (Solo se muestra si hay texto)
        rx.cond(
            BaseState.search_query != "",
            rx.box(
                rx.cond(
                    BaseState.search_results.length() > 0,
                    # Si hay resultados, mostramos la lista
                    rx.vstack(
                        rx.foreach(
                            BaseState.search_results,
                            lambda res: render_search_result(res)
                        ),
                        width="100%",
                        spacing="1",
                    ),
                    # Si no hay resultados
                    rx.text("No se encontraron módulos.", padding="3", size="2", color_scheme="gray")
                ),
                # Estilos para que flote debajo del input
                position="absolute",
                top="100%",
                left="0",
                margin_top="2",
                width="100%",
                background_color="white",
                border_radius="md",
                box_shadow="0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
                z_index="50",
                padding="2",
            )
        ),
        position="relative", # Fundamental para que el menú flotante este bien posicionado
    )