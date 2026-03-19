from typing import Dict

# Definimos los bloques de teoría específicos para este formulario
THEORY_BLOCKS: Dict[str, Dict[str, str]] = {
    "vrdc": {
        "title": "Resistencia a Cortante (Vrd,c)",
        "reference": "EC2 Art. 6.2.2",
        "content": """
La resistencia de diseño a cortante de una sección sin armadura de cortante viene dada por:

$$V_{Rd,c} = [C_{Rd,c} \cdot k \cdot (100 \cdot \rho_l \cdot f_{ck})^{1/3} + k_1 \cdot \sigma_{cp}] \cdot b_w \cdot d$$

Donde:
* **k**: Factor de escala $1 + \sqrt{200/d} \le 2.0$.
* **ρl**: Cuantía de armadura traccionada.
* **bw**: En secciones circulares, se toma el ancho medio de la sección.
        """
    }
}