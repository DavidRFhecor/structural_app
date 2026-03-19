import reflex as rx

def beam_sketch(h, b_top, t_top, b_bot, t_bot, tw) -> rx.Component:
    """Genera un croquis SVG reactivo de la sección Doble T."""
    # Coordenadas simplificadas para el dibujo
    # h_draw, b_t_draw, etc., escalados para el visor
    scale = 0.2
    sh = h * scale
    sbt = b_top * scale
    stt = t_top * scale
    sbb = b_bot * scale
    stb = t_bot * scale
    stw = tw * scale
    
    mid = 150 # Centro del lienzo
    
    return rx.svg(
        # Ala Superior
        rx.rect(x=mid - sbt/2, y=20, width=sbt, height=stt, fill="#CBD5E0", stroke="#4A5568"),
        # Alma
        rx.rect(x=mid - stw/2, y=20+stt, width=stw, height=sh-stt-stb, fill="#CBD5E0", stroke="#4A5568"),
        # Ala Inferior
        rx.rect(x=mid - sbb/2, y=20+sh-stb, width=sbb, height=stb, fill="#CBD5E0", stroke="#4A5568"),
        view_box="0 0 300 300",
        width="100%",
        height="300px",
    )