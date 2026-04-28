from pydantic import BaseModel, Field
from structural_app.shared.domain.result_models import SolverResponse, CheckResult

# 1. Asegúrate de que el modelo coincida con los IDs de tu config.json
class MuroInput(BaseModel):
    h_muro: float
    b_zapata: float
    ved: float

def calculate_element(payload: dict) -> SolverResponse:
    """Adaptador REAL para el cálculo de estabilidad de muros."""
    payload.pop("_features", None)
    
    # 2. Validamos y extraemos los datos que vienen del formulario
    try:
        data = MuroInput(**payload)
    except Exception as e:
        return SolverResponse(is_ok=False, summary=f"Error en datos: {str(e)}", checks=[])

    # 3. LÓGICA DE CÁLCULO REAL (Simplificada para el ejemplo)
    # Ejemplo: El factor de vuelco mejora si la zapata es más ancha y empeora si el muro es más alto
    factor_vuelco_estimado = (data.b_zapata * 1.5) / (data.h_muro * 0.5) 
    
    # Ejemplo: El deslizamiento depende del cortante (ved)
    # A más cortante (ved), menor factor de seguridad
    factor_deslizamiento_estimado = 500 / (data.ved + 1) 

    # 4. Asignamos los valores calculados a los resultados
    checks = [
        CheckResult(
            description="Estabilidad al Vuelco",
            status=factor_vuelco_estimado >= 1.5,
            value=round(factor_vuelco_estimado, 2),
            limit=1.5,
            unit="FS"
        ),
        CheckResult(
            description="Estabilidad al Deslizamiento",
            status=factor_deslizamiento_estimado >= 1.5,
            value=round(factor_deslizamiento_estimado, 2),
            limit=1.5,
            unit="FS"
        )
    ]
    
    return SolverResponse(
        is_ok=all(c.status for c in checks),
        summary="Cálculo actualizado con datos del formulario.",
        checks=checks
    )