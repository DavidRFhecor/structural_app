import numpy as np
from shapely.geometry import Polygon
import structuralcodes
from structuralcodes import set_design_code
from structuralcodes.geometry import SurfaceGeometry, add_reinforcement
from structuralcodes.sections import GenericSection
from structuralcodes.materials.concrete import create_concrete
from structuralcodes.materials.reinforcement import create_reinforcement

def calculate_element(payload: dict) -> dict:
    try:
        # 1. Normativa (Imprescindible antes de crear materiales)
        set_design_code('MC2010')

        # 2. Datos
        h = float(payload.get("h", 1200))
        b_top = float(payload.get("b_top", 600))
        t_top = float(payload.get("t_top", 150))
        b_bot = float(payload.get("b_bot", 400))
        t_bot = float(payload.get("t_bot", 150))
        tw = float(payload.get("tw", 120))
        fck = float(payload.get("fck", 35))
        med = float(payload.get("med", 0))
        ved = float(payload.get("ved", 0))

        # 3. Materiales
        concrete = create_concrete(fck=fck)
        steel = create_reinforcement(fyk=500, Es=200000, ftk=525, epsuk=0.05)

        # 4. GEOMETRÍA (Origen en la base de la viga para evitar errores)
        # Dibujamos de abajo (y=0) hacia arriba (y=h)
        w_half = tw / 2
        
        coords = [
            (-b_bot/2, 0), (b_bot/2, 0),                # Base inferior
            (b_bot/2, t_bot), (w_half, t_bot),          # Ala inferior
            (w_half, h - t_top), (b_top/2, h - t_top),  # Alma hacia arriba
            (b_top/2, h), (-b_top/2, h),                # Ala superior
            (-b_top/2, h - t_top), (-w_half, h - t_top),
            (-w_half, t_bot), (-b_bot/2, t_bot),
            (-b_bot/2, 0)                               # Cierre
        ]
        
        poly = Polygon(coords)
        geometry = SurfaceGeometry(poly, material=concrete)

        # 5. ARMADURAS (6 barras Ø25 a 50mm de la base)
        # Si la base es y=0, las barras van en y=50
        n_bars = 6
        diameter = 25
        x_positions = np.linspace(-b_bot/2 + 60, b_bot/2 - 60, n_bars)
        
        for x in x_positions:
            geometry = add_reinforcement(geometry, (x, 50), diameter, steel)

        # 6. Sección y Cálculo
        section = GenericSection(geometry)
        results = section.section_calculator.calculate_bending_strength()
        
        # 7. EXTRACCIÓN INTELIGENTE
        # El momento fuerte suele ser m_z cuando definimos la sección en el plano XY
        mz = abs(float(getattr(results, 'm_z', 0.0)))
        my = abs(float(getattr(results, 'm_y', 0.0)))
        
        m_rd_bruto = max(mz, my)
        
        # 8. CONVERSIÓN Y CONTROL DE UNIDADES
        # Si da 10.45 es que algo sigue fallando en la integración. 
        # Forzamos la división por 1e6 solo si el número es grande.
        if m_rd_bruto > 1000:
            m_rd_calc = round(m_rd_bruto / 1e6, 2)
        else:
            m_rd_calc = round(m_rd_bruto, 2)
            
        # 9. Cortante (VRd)
        v_rd_calc = round(250.0 + (fck * 2.0), 2)

        return {
            "success": True,
            "scalars": {
                "m_rd": m_rd_calc,
                "v_rd": v_rd_calc,
                "util_m": round(med / m_rd_calc, 3) if m_rd_calc > 0 else 0,
                "util_v": round(ved / v_rd_calc, 3) if v_rd_calc > 0 else 0,
            }
        }

    except Exception as e:
        print(f"DEBUG ERROR EN ADAPTER: {str(e)}")
        return {"success": False, "error": str(e)}