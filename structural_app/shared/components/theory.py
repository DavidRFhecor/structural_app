import reflex as rx

def theory_popover(title: str, content: str, reference: str = ""):
    """Crea un icono de información que despliega la base normativa."""
    return rx.popover.root(
        rx.popover.trigger(
            rx.icon("info", size=16, color="blue", cursor="pointer"),
        ),
        rx.popover.content(
            rx.vstack(
                rx.hstack(
                    rx.text(title, weight="bold", size="3"),
                    rx.spacer(),
                    rx.badge(reference, color_scheme="blue", variant="surface"),
                    width="100%",
                ),
                rx.divider(),
                rx.markdown(content),
                spacing="3",
            ),
            width="400px",
        ),
    )