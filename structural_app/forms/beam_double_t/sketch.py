import reflex as rx

def beam_sketch(h, b_top, t_top, b_bot, t_bot, tw) -> rx.Component:
    """Genera un croquis SVG reactivo de la sección Doble T corregido para tipos Var."""
    
    # Definimos el escalado como Var
    scale = 0.2
    mid = 150

    # Realizamos las operaciones y las convertimos a String para evitar el error de tipos
    # Usamos .to(str) al final de cada cálculo de prop
    
    return rx.el.svg(
        # Ala Superior
        rx.el.rect(
            x=(mid - (b_top * scale) / 2).to(str), 
            y="20", 
            width=(b_top * scale).to(str), 
            height=(t_top * scale).to(str), 
            fill="#CBD5E0", 
            stroke="#4A5568"
        ),
        # Alma
        rx.el.rect(
            x=(mid - (tw * scale) / 2).to(str), 
            y=(20 + (t_top * scale)).to(str), 
            width=(tw * scale).to(str), 
            height=((h - t_top - t_bot) * scale).to(str), 
            fill="#CBD5E0", 
            stroke="#4A5568"
        ),
        # Ala Inferior
        rx.el.rect(
            x=(mid - (b_bot * scale) / 2).to(str), 
            y=(20 + (h - t_bot) * scale).to(str), 
            width=(b_bot * scale).to(str), 
            height=(t_bot * scale).to(str), 
            fill="#CBD5E0", 
            stroke="#4A5568"
        ),
        view_box="0 0 300 300",
        width="100%",
        height="300px",
    )