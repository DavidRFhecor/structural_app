import numpy as np
# IMPORTANTE: Nueva importación
from shapely.geometry import Polygon 
from structuralcodes.sections import GenericSection as Section
from structuralcodes.geometry import SurfaceGeometry 
from structuralcodes.materials.concrete import ConcreteMC2010
from structuralcodes.materials.reinforcement import ReinforcementMC2010

def calculate_element(payload: dict) -> dict:
    try:
        # 1. Datos (Igual que antes)
        h = float(payload.get("h", 1200))
        b_top = float(payload.get("b_top", 600))
        t_top = float(payload.get("t_top", 150))
        b_bot = float(payload.get("b_bot", 400))
        t_bot = float(payload.get("t_bot", 150))
        tw = float(payload.get("tw", 120))
        fck = float(payload.get("fck", 35))
        med = float(payload.get("med", 0))
        ved = float(payload.get("ved", 0))

        # 2. Materiales
        concrete = ConcreteMC2010(fck)
        
        # 3. Geometría (Cerrando el Polígono)
        w_half = tw / 2
        bt_half = b_top / 2
        bb_half = b_bot / 2

        # Lista de puntos original
        points = [
            (-bt_half, 0), (bt_half, 0),
            (bt_half, t_top), (w_half, t_top),
            (w_half, h - t_bot), (bb_half, h - t_bot),
            (bb_half, h), (-bb_half, h),
            (-bb_half, h - t_bot), (-w_half, h - t_bot),
            (-w_half, t_top), (-bt_half, t_top),
            (-bt_half, 0) # <--- PUNTO DE CIERRE: Volvemos al inicio
        ]

        # CREAMOS EL OBJETO SHAPELY QUE PIDE LA LIBRERÍA
        poly = Polygon(points)

        # PASAMOS EL OBJETO POLY A SURFACEGEOMETRY
        geometry = SurfaceGeometry(poly=poly, material=concrete)

        # 4. Sección
        section = Section(geometry=geometry, material=concrete)
        
        # 5. Ratios de prueba
        m_rd_calc = 850.5
        v_rd_calc = 420.0
        util_m = round(med / m_rd_calc, 3) if m_rd_calc > 0 else 0
        util_v = round(ved / v_rd_calc, 3) if v_rd_calc > 0 else 0

        return {
            "success": True,
            "scalars": {
                "m_rd": m_rd_calc,
                "v_rd": v_rd_calc,
                "util_m": util_m,
                "util_v": util_v,
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error en el adaptador de Doble T: {str(e)}"
        }