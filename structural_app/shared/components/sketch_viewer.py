import reflex as rx

def sketch_viewer(state_ptr: any):
    return rx.cond(
        state_ptr.active_form_config.features.get("sketch", False),
        rx.vstack(
            rx.heading("Croquis de Referencia", size="3", mb="2"),
            rx.box(
                rx.image(
                    src=rx.cond(
                        state_ptr.current_form_key != "",
                        f"/sketches/{state_ptr.current_form_key}.png",
                        ""
                    ),
                    # Forzamos a que la imagen llene el contenedor
                    width="100%",
                    height="100%",
                    # 'contain' mantiene la proporción sin deformar ni cortar
                    object_fit="contain", 
                ),
                # Aquí defines el tamaño estándar para TODOS los croquis
                width="100%",
                height="300px", # Ajusta esta altura a tu gusto
                display="flex",
                align_items="center",
                justify_content="center",
                background_color="var(--gray-2)", # Fondo neutro por si la imagen es estrecha
                border_radius="md",
                overflow="hidden",
                border="1px solid var(--gray-5)"
            ),
            padding="4",
            background="white",
            border_radius="lg",
            margin_top="4",
            width="100%"
        )
    )