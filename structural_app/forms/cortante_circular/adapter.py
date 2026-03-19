from .dto import CortanteCircularDTO
from ...shared.domain.result_models import SolverResponse, CheckResult
# Aquí importarías el motor real de GitHub:
# from fhecor_structuralcodes.checks_ec2_2004 import check_shear_circular

async def calculate_element(dto: CortanteCircularDTO) -> SolverResponse:
    """Traduce el DTO al motor externo y formatea la respuesta."""
    
    # 1. Simulación de llamada al motor externo (fhecor_structuralcodes)
    # En producción: result_externo = check_shear_circular(d=dto.diametro, ...)
    
    v_rdc = 180.5 # Valor que vendría del motor
    cumple = v_rdc >= dto.ved
    
    # 2. Mapeo a nuestro formato estándar de resultados
    check_cortante = CheckResult(
        description="Resistencia a cortante del hormigón (Vrd,c)",
        status=cumple,
        value=dto.ved,
        limit=v_rdc,
        unit="kN",
        ratio=dto.ved / v_rdc if v_rdc > 0 else 0,
        reference="EC2 Art. 6.2.2"
    )

    return SolverResponse(
        is_ok=cumple,
        checks=[check_cortante],
        summary="Cálculo finalizado según Eurocódigo 2.",
        metadata={"solver": "EC2_2004_Standard"}
    )