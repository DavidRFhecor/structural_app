import numpy as np

class Geometry3DUtils:
    """Generador de geometrías básicas para ingeniería estructural."""

    @staticmethod
    def create_box_mesh(width: float, height: float, depth: float):
        """Genera vértices y caras para un paralelepípedo (vigas, muros)."""
        # Definición de los 8 vértices
        v = np.array([
            [0, 0, 0], [width, 0, 0], [width, height, 0], [0, height, 0],
            [0, 0, depth], [width, 0, depth], [width, height, depth], [0, height, depth]
        ])
        # Definición de las 12 caras triangulares
        f = [
            [0, 1, 2], [0, 2, 3], [4, 5, 6], [4, 6, 7], # Tapas
            [0, 1, 5], [0, 5, 4], [1, 2, 6], [1, 6, 5], # Lados
            [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7]  # Lados
        ]
        return {"vertices": v.tolist(), "faces": f}

    @staticmethod
    def create_cylinder_mesh(radius: float, height: float, segments: int = 16):
        """Genera vértices para secciones circulares (pilares)."""
        # Lógica para generar cilindro...
        return {"type": "cylinder", "radius": radius, "height": height}