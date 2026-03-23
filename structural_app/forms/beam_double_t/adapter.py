from structural_app.forms.beam_double_t.dto import BeamDoubleTInputs
from structural_app.shared.domain.result_models import SolverResponse, CheckResult
from fhecor_structuralcodes.checks_ec2_2004 import crack_width, shear_cheks

def calculate_element(payload: dict) -> SolverResponse:
    try:
        data = BeamDoubleTInputs(**payload)
        
        # 1. Cálculo de Fisuración
        res_fisura, _ = crack_width(
            b=data.b_top, h=data.h, fck=data.fck, c=40.0,
            sigma_s=250.0, As=1000.0, phi_eq=20.0
        )
        wk = res_fisura.get('wk', 0.0)

        # 2. Cálculo de Cortante (Nuevo)
        # Calculamos d y z aproximados para la sección
        d_eff = data.h - 50
        z_eff = 0.9 * d_eff
        
        res_shear, _ = shear_cheks(
            ved=data.ved * 1000, fck=data.fck, fyk=500,
            asw=0, s=1, z=z_eff, theta=45.0, d=d_eff,
            asl=1000, bw=data.tw, ned=0, Ac=data.h * data.tw,
            sismic_comb=False
        )
        vrd_cap = res_shear.get('VRdc', 0.0) / 1000  # Convertimos a kN

        return SolverResponse(
            is_ok=wk <= 0.3 and (data.ved <= vrd_cap),
            summary="Cálculo de flexión y cortante completado.",
            checks=[
                CheckResult(
                    description="Fisuración (wk)",
                    status=wk <= 0.3,
                    value=round(wk, 3),
                    limit=0.3, unit="mm",
                    ratio=round(wk/0.3, 2)
                ),
                CheckResult(
                    description="Agotamiento Cortante (VRd)",
                    status=data.ved <= vrd_cap,
                    value=data.ved,
                    limit=round(vrd_cap, 2),
                    unit="kN",
                    ratio=round(data.ved / vrd_cap, 2) if vrd_cap > 0 else 0
                )
            ]
        )
    except Exception as e:
        return SolverResponse(is_ok=False, summary=str(e))