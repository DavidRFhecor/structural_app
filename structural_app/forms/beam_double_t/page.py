import reflex as rx
from structural_app.shared.components.layout import main_layout
from structural_app.forms.beam_double_t.state import BeamDoubleTState
from structural_app.forms.beam_double_t.sketch import beam_sketch

def input_panel():
    """Panel lateral de parámetros de entrada."""
    return rx.vstack(
        rx.heading("Parámetros de Diseño", size="5"),
        rx.divider(),
        
        rx.text("Geometría Sección (mm)", weight="bold", size="3"),
        
        rx.grid(
            # Canto Total - Usa el setter específico set_h
            rx.vstack(
                rx.text("Canto (h)", size="2"),
                rx.input(
                    value=BeamDoubleTState.h.to(str), 
                    on_change=BeamDoubleTState.set_h, 
                    type="number",
                    placeholder="1200"
                ),
                align_items="start"
            ),
            # Ancho Ala Superior - Usa set_value genérico
            rx.vstack(
                rx.text("Ancho Sup (b_top)", size="2"),
                rx.input(
                    value=BeamDoubleTState.b_top.to(str), 
                    on_change=lambda v: BeamDoubleTState.set_value("b_top", v), 
                    type="number"
                ),
                align_items="start"
            ),
            # Espesor Ala Superior
            rx.vstack(
                rx.text("Espesor Sup (t_top)", size="2"),
                rx.input(
                    value=BeamDoubleTState.t_top.to(str), 
                    on_change=lambda v: BeamDoubleTState.set_value("t_top", v), 
                    type="number"
                ),
                align_items="start"
            ),
            # Espesor Alma
            rx.vstack(
                rx.text("Espesor Alma (tw)", size="2"),
                rx.input(
                    value=BeamDoubleTState.tw.to(str), 
                    on_change=lambda v: BeamDoubleTState.set_value("tw", v), 
                    type="number"
                ),
                align_items="start"
            ),
            # Ancho Ala Inferior
            rx.vstack(
                rx.text("Ancho Inf (b_bot)", size="2"),
                rx.input(
                    value=BeamDoubleTState.b_bot.to(str), 
                    on_change=lambda v: BeamDoubleTState.set_value("b_bot", v), 
                    type="number"
                ),
                align_items="start"
            ),
            # Espesor Ala Inferior
            rx.vstack(
                rx.text("Espesor Inf (t_bot)", size="2"),
                rx.input(
                    value=BeamDoubleTState.t_bot.to(str), 
                    on_change=lambda v: BeamDoubleTState.set_value("t_bot", v), 
                    type="number"
                ),
                align_items="start"
            ),
            columns="2", spacing="3", width="100%"
        ),

        rx.divider(),
        rx.text("Esfuerzos Solicitantes", weight="bold", size="3"),
        
        rx.hstack(
            rx.vstack(
                rx.text("Med (kNm)", size="2"), 
                rx.input(
                    value=BeamDoubleTState.med.to(str), 
                    on_change=lambda v: BeamDoubleTState.set_value("med", v), 
                    type="number"
                ),
                align_items="start"
            ),
            rx.vstack(
                rx.text("Ved (kN)", size="2"), 
                rx.input(
                    value=BeamDoubleTState.ved.to(str), 
                    on_change=lambda v: BeamDoubleTState.set_value("ved", v), 
                    type="number"
                ),
                align_items="start"
            ),
            width="100%", spacing="3"
        ),

        rx.button(
            "Ejecutar Cálculo", 
            on_click=BeamDoubleTState.run_calculation,
            loading=BeamDoubleTState.is_calculating,
            width="100%", color_scheme="blue",
            margin_top="4"
        ),
        spacing="4", width="100%"
    )

def result_panel():
    """Panel derecho de resultados y croquis."""
    # Convertimos a entero para la barra de progreso
    progress_val = (BeamDoubleTState.util_m * 100).to(int)
    
    return rx.vstack(
        rx.heading("Verificación Estructural", size="5"),
        
        # Croquis de la sección
        rx.box(
            beam_sketch(
                BeamDoubleTState.h, BeamDoubleTState.b_top, BeamDoubleTState.t_top,
                BeamDoubleTState.b_bot, BeamDoubleTState.t_bot, BeamDoubleTState.tw
            ),
            width="100%", border="1px solid #E5E7EB", bg="white", border_radius="lg", padding="2"
        ),
        
        # Tarjetas de Capacidad Resistente (MRd, VRd)
        rx.grid(
            rx.card(
                rx.vstack(
                    rx.text("MRd (Capacidad)", size="1", color_scheme="gray"),
                    rx.text(f"{BeamDoubleTState.m_rd} kNm", weight="bold", size="4"),
                    align_items="start"
                )
            ),
            rx.card(
                rx.vstack(
                    rx.text("VRd (Capacidad)", size="1", color_scheme="gray"),
                    rx.text(f"{BeamDoubleTState.v_rd} kN", weight="bold", size="4"),
                    align_items="start"
                )
            ),
            columns="2", spacing="4", width="100%"
        ),
        
        # Barra de Ratio de Agotamiento
        rx.vstack(
            rx.hstack(
                rx.text("Ratio de Agotamiento (Med/MRd)", size="2"),
                rx.spacer(),
                rx.badge(
                    rx.cond(BeamDoubleTState.util_m > 0, f"{progress_val}%", "0%"), 
                    color_scheme=rx.cond(BeamDoubleTState.util_m > 1, "red", "green"),
                    variant="surface"
                ),
                width="100%"
            ),
            rx.progress(
                value=progress_val, 
                color_scheme=rx.cond(BeamDoubleTState.util_m > 1, "red", "green"), 
                width="100%"
            ),
            width="100%", spacing="2"
        ),
        spacing="6", width="100%"
    )

def beam_double_t_page():
    """Página principal del formulario."""
    return main_layout(
        rx.grid(
            rx.card(input_panel(), padding="4"),
            rx.card(result_panel(), padding="4"),
            columns="2",
            spacing="6",
            grid_template_columns="1fr 1.5fr",
            width="100%",
            on_mount=BeamDoubleTState.on_load 
        )
    )