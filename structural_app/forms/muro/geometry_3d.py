from structural_app.shared.services.geometry_3d_utils import Geometry3DUtils

def generate_muro_3d_payload(state):
    """Genera la malla 3D compuesta por zapata y alzado."""
    # 1. Malla de la Zapata (Box)
    zapata = Geometry3DUtils.create_box_mesh(
        width=state.b_zapata, 
        height=state.h_zapata, 
        depth=5.0  # Profundidad unitaria para visualización
    )
    
    # 2. Malla del Alzado (Trapézio simplificado como Box para esta versión)
    alzado = Geometry3DUtils.create_box_mesh(
        width=state.e_inferior,
        height=state.h_muro,
        depth=5.0
    )
    # Traslación del alzado sobre la zapata
    for v in alzado["vertices"]:
        v[0] += state.c_puntera
        v[1] += state.h_zapata

    return {
        "meshes": [
            {"data": zapata, "color": "#A0AEC0", "name": "Zapata"},
            {"data": alzado, "color": "#CBD5E0", "name": "Alzado"}
        ]
    }