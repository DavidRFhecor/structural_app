import math
from structural_app.forms.cortante_circular.dto import CortanteCircularDTO
from structural_app.shared.domain.result_models import SolverResponse, CheckResult
# Importación desde tu repositorio FHECOR
from fhecor_structuralcodes.checks_ec2_2004 import shear_cheks

def calculate_element(payload: dict) -> SolverResponse:
    try:
        # Convertimos el diccionario recibido a DTO
        data = CortanteCircularDTO(**payload)
        
        # Conversión a unidades del motor (N, mm)
        d = data.diametro - data.recubrimiento
        Ac = (math.pi * (data.diametro**2)) / 4
        z = 0.9 * d 
        
        # Llamada a la lógica de FHECOR (shear_cheks)
        # Ajustamos 'asl' para que use 'as_principal' del DTO
        results, logs = shear_cheks(
            ved=data.ved * 1000, 
            fck=data.fck, 
            fyk=500,
            asw=0, 
            s=1, 
            z=z, 
            theta=45.0, 
            d=d,
            asl=data.as_principal, # Corregido: antes era as_longitudinal
            bw=data.diametro,
            ned=0, 
            Ac=Ac, 
            sismic_comb=False
        )

        vrdc_kn = results['VRdc'] / 1000
        ratio = data.ved / vrdc_kn if vrdc_kn > 0 else 0
        capacidad_vrdc = results['VRdc'] / 1000  # Convertimos N a kN
        
        return SolverResponse(
            is_ok=data.ved <= capacidad_vrdc,
            summary="Cálculo de cortante finalizado.",
            checks=[
                CheckResult(
                    description="Resistencia Cortante (VRdc)",
                    status=data.ved <= capacidad_vrdc,
                    value=round(data.ved, 2),        # Lo que solicita el usuario
                    limit=round(capacidad_vrdc, 2),  # Lo que resiste el hormigón
                    unit="kN",
                    ratio=round(data.ved / capacidad_vrdc, 2) if capacidad_vrdc > 0 else 0
                )
            ]
        )
    except Exception as e:
        return SolverResponse(is_ok=False, summary=f"Error en adaptador: {str(e)}")