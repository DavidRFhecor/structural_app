from .dto import ElementDTO
from ....shared.domain.result_models import SolverResponse, CheckResult
# Importar aquí el motor externo:
# from fhecor_structuralcodes.EN1992 import check_function

async def calculate_element(dto: ElementDTO) -> SolverResponse:
    """Traduce el DTO al motor externo y normaliza la salida."""
    
    # 1. Llamada al motor (Simulada)
    # raw_result = check_function(b=dto.ancho, h=dto.canto, ...)
    
    # 2. Mapeo a CheckResult (Estandarización ELU/ELS)
    check_geometria = CheckResult(
        description="Esbeltez de la sección",
        status=True,
        value=dto.canto / dto.ancho,
        limit=4.0,
        unit="",
        ratio=(dto.canto / dto.ancho) / 4.0,
        reference="Criterio de diseño"
    )

    return SolverResponse(
        is_ok=True,
        checks=[check_geometria],
        summary="Cálculo completado correctamente.",
        metadata={"engine_version": "v1.0.0"}
    )