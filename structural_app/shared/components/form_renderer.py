import reflex as rx

def render_field(field: rx.Var, state_ptr: any):
    """Renderiza un campo individual."""
    return rx.vstack(
        rx.text(field["label"], size="2"),
        rx.input(
            placeholder=field["unit"],
            on_blur=lambda v: state_ptr.set_value(field["id"], v),
            width="100%",
        ),
        align_items="start",
    )

def render_group(group: rx.Var, state_ptr: any):
    """Renderiza un grupo y sus campos."""
    return rx.vstack(
        rx.text(group["name"], weight="bold", margin_top="4"),
        rx.grid(
            # Iteramos sobre los campos del grupo
            rx.foreach(
                group["fields"],
                lambda field: render_field(field, state_ptr)
            ),
            columns="2",
            spacing="4",
            width="100%",
        ),
        width="100%",
        align_items="start",
    )

def render_dynamic_form(config: rx.Var, state_ptr: any):
    """Punto de entrada principal del formulario."""
    return rx.vstack(
        rx.heading(config.title, size="6"),
        rx.text(config.description, color_scheme="gray"),
        rx.divider(),
        
        # Iteramos sobre los grupos
        rx.foreach(
            config.groups,
            lambda group: render_group(group, state_ptr)
        ),
        
        rx.button(
            "Calcular", 
            on_click=state_ptr.calculate,
            is_loading=state_ptr.is_calculating,
            width="100%",
            color_scheme="blue",
            margin_top="6",
        ),
        width="100%",
        spacing="4",
    )