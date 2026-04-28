import reflex as rx

def render_form_header(config: rx.Var):
    """Renderiza el título y mueve la descripción a un popover."""
    return rx.vstack(
        rx.hstack(
            rx.heading(config["title"], size="7"),
            rx.popover.root(
                rx.popover.trigger(
                    rx.icon(
                        "info", 
                        size=20, 
                        color="var(--blue-9)",
                        cursor="pointer",
                        style={"_hover": {"opacity": 0.7}}
                    ),
                ),
                rx.popover.content(
                    rx.text(config.get("description", "Sin descripción."), size="2"),
                    rx.popover.close(
                        rx.button("Cerrar", size="1", variant="soft", mt="2")
                    ),
                    style={"max_width": "300px"},
                ),
            ),
            align="center",
            spacing="3",
        ),
        rx.divider(),
        width="100%",
        mb="4",
    )

def render_field(field: rx.Var, state_ptr: any):
    """Renderiza un campo que se adapta: tabla en PC, apilado en móvil."""
    val = state_ptr.form_data[field["id"]]
    is_error = (val == "")
    
    return rx.grid(
        rx.text(
            field["label"], 
            size="2", 
            weight="medium", 
            width={"sm": "100%", "md": "200px"},
            mb={"sm": "1", "md": "0"}
        ),
        rx.hstack(
            rx.input(
                default_value=field["default"].to(str),
                on_blur=lambda v: state_ptr.set_value(field["id"], v),
                width={"sm": "100%", "md": "120px"},
                variant="surface",
                border=rx.cond(is_error, "1px solid var(--red-8)", "1px solid var(--gray-6)"),
            ),
            rx.text(field["unit"], size="2", color_scheme="gray", width="40px"),
            spacing="2",
            align="center",
            width="100%",
        ),
        columns={"sm": "1", "md": "2"},
        align="center",
        width="100%",
        padding_y="2",
        border_bottom="1px solid var(--gray-3)",
    )

def render_group(group: rx.Var, state_ptr: any):
    """Contenedor de grupo que ahora SÍ incluye los campos."""
    return rx.vstack(
        rx.text(
            group["name"], 
            size="3", 
            weight="bold", 
            color="rgb(0, 50, 100)", 
            mt="4", 
            mb="2"
        ),

        rx.foreach(
            group["fields"],
            lambda field: render_field(field, state_ptr)
        ),
        width="100%",
        background="var(--gray-2)",
        padding="4",
        border_radius="lg",
    )
def render_dynamic_form(config: rx.Var, state_ptr: any):
    """Punto de entrada principal."""
    return rx.vstack(
        render_form_header(config),
        rx.foreach(
            config["groups"],
            lambda group: render_group(group, state_ptr)
        ),
        rx.button(
            "Calcular", 
            on_click=state_ptr.calculate,
            is_loading=state_ptr.is_calculating,
            width="100%",
            size="3",
            color_scheme="blue",
            margin_top="6",
        ),
        width="100%",
        spacing="2",
    )