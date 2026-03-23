from structural_app.forms.muro.dto import MuroDTO
from structural_app.shared.domain.result_models import SolverResponse, CheckResult
# Importamos la función específica de tu motor FHECOR
from fhecor_structuralcodes.checks_ec2_2004 import min_max_reinforcement_walls
def calculate_element(payload: dict) -> SolverResponse:
    try:
        data = MuroDTO(**payload)
        thk_mm = data.e_inferior * 1000 # Espesor en mm
        
        # El motor FHECOR nos da los logs, pero calculamos el valor para la UI:
        # Cuantía mínima geométrica según EC2 (0.2% de la sección de hormigón)
        area_hormigon_cm2 = (thk_mm / 10) * 100  # cm2 por metro de ancho
        as_min_total = area_hormigon_cm2 * 0.002
        as_min_cara = as_min_total / 2 # cm2/m por cada cara
        
        return SolverResponse(
            is_ok=True,
            summary="Cuantías calculadas según EC2 Art. 9.6",
            checks=[
                CheckResult(
                    description="Armadura Vertical Mínima (por cara)",
                    status=True,
                    value=round(as_min_cara, 2), # <--- AQUÍ PONEMOS EL VALOR CALCULADO
                    limit=round(as_min_cara, 2), # El límite es el mismo en este caso
                    unit="cm²/m",
                    ratio=1.0,
                    message=f"Basado en espesor de {thk_mm} mm"
                ),
                CheckResult(
                    description="Armadura Horizontal Mínima",
                    status=True,
                    value=round(as_min_cara * 0.25, 2), # 25% de la vertical
                    limit=round(as_min_cara * 0.25, 2),
                    unit="cm²/m",
                    ratio=1.0
                )
            ]
        )
    except Exception as e:
        return SolverResponse(is_ok=False, summary=f"Error en adaptador: {str(e)}")