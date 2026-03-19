import reflex as rx

def viewer_3d_shell(payload: rx.Var):
    """
    Contenedor para el visor 3D. 
    Recibe un payload (vértices, caras, colores) desde el State.
    """
    return rx.cond(
        payload,  # Si hay datos 3D
        rx.vstack(
            rx.box(
                # Aquí se integraría el componente Three.js/Plotly real
                rx.center(
                    rx.vstack(
                        rx.icon(tag="box", size=40, color="gray"),
                        rx.text("Renderizado 3D Activo", color="gray", size="2"),
                        spacing="2",
                    ),
                    height="400px",
                    width="100%",
                    bg="blackAlpha.50",
                    border_radius="md",
                ),
                width="100%",
            ),
            rx.text("Use el ratón para rotar y hacer zoom en el elemento.", size="1", color_scheme="gray"),
            width="100%",
        ),
        # Fallback si el formulario no tiene 3D o no se ha calculado
        rx.center(
            rx.text("Vista 3D no disponible para este elemento", color="gray", font_style="italic"),
            height="200px",
            width="100%",
            border="1px dashed #e5e7eb",
            border_radius="md",
        )
    )