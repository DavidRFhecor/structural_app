import math

class SketchUtils:
    """Utilidades para generar elementos geométricos en SVG."""
    
    @staticmethod
    def get_viewbox(width: float, height: float, padding: float = 20):
        """Calcula el ViewBox centrado con padding."""
        return f"-{padding} -{padding} {width + 2*padding} {height + 2*padding}"

    @staticmethod
    def polar_to_cartesian(cx, cy, radius, angle_deg):
        """Convierte coordenadas polares a cartesianas para dibujar armaduras circulares."""
        angle_rad = math.radians(angle_deg)
        return (
            cx + radius * math.cos(angle_rad),
            cy + radius * math.sin(angle_rad)
        )