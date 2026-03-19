import reflex as rx
from structural_app.shared.components.layout import dashboard_layout
from structural_app.shared.components.theory import theory_popover
from structural_app.forms.beam_double_t.state import BeamDoubleTState
from structural_app.forms.beam_double_t.sketch import beam_sketch

def input_panel_component():
    return rx.vstack(
        rx.heading("Parámetros de Diseño", size="5"),
        rx.divider(),
        rx.text("Geometría Sección (mm)", weight="bold"),
        rx.number_input(label="Canto Total (h)", value=BeamDoubleTState.h, on_change=BeamDoubleTState.set_h),
        rx.number_input(label="Ancho Ala Sup (b_top)", value=BeamDoubleTState.b_top, on_change=BeamDoubleTState.set_b_top),
        rx.number_input(label="Ancho Ala Inf (b_bot)", value=BeamDoubleTState.b_bot, on_change=BeamDoubleTState.set_b_bot),
        
        rx.divider(),
        rx.text("Esfuerzos Solicitantes", weight="bold"),
        rx.number_input(label="M_Ed (kNm)", value=BeamDoubleTState.med, on_change=BeamDoubleTState.set_med),
        rx.number_input(label="V_Ed (kN)", value=BeamDoubleTState.ved, on_change=BeamDoubleTState.set_ved),
        
        rx.button(
            "Ejecutar Cálculo", 
            on_click=BeamDoubleTState.run_calculation,
            loading=BeamDoubleTState.is_calculating,
            width="100%", color_scheme="blue"
        ),
        spacing="4",
    )

def result_panel_component():
    return rx.vstack(
        rx.heading("Verificación Estructural", size="5"),
        # Render del croquis SVG dinámico
        rx.box(
            beam_sketch(
                BeamDoubleTState.h, BeamDoubleTState.b_top, BeamDoubleTState.t_top,
                BeamDoubleTState.b_bot, BeamDoubleTState.t_bot, BeamDoubleTState.tw
            ),
            width="100%", border="1px solid #E5E7EB", bg="white", border_radius="lg"
        ),
        
        # Tarjetas de resultados
        rx.grid(
            rx.card(rx.stat(rx.stat_label("MRd"), rx.stat_number(f"{BeamDoubleTState.m_rd} kNm"))),
            rx.card(rx.stat(rx.stat_label("VRd"), rx.stat_number(f"{BeamDoubleTState.v_rd} kN"))),
            columns="2", spacing="4", width="100%"
        ),
        
        # Check visual de utilización
        rx.vstack(
            rx.hbox(
                rx.text("Ratio de Flexión (MEd/MRd)", size="2"),
                rx.spacer(),
                rx.badge(f"{BeamDoubleTState.util_m * 100}%", color_scheme="red" if BeamDoubleTState.util_m > 1 else "green"),
                width="100%"
            ),
            rx.progress(value=BeamDoubleTState.util_m * 100, color_scheme="red" if BeamDoubleTState.util_m > 1 else "green", width="100%"),
            width="100%", spacing="2"
        ),
        spacing="6", width="100%"
    )

def beam_double_t_page():
    """Página del formulario usando el layout 40/60."""
    return dashboard_layout(input_panel_component(), result_panel_component())