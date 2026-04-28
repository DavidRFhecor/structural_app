from pydantic import BaseModel, Field, ValidationError
from structural_app.shared.domain.result_models import SolverResponse, CheckResult
from fhecor_structuralcodes.checks_ec2_2004 import crack_width, shear_cheks

# DEFINICIÓN DEL MODELO DE ENTRADA
class InputModel(BaseModel):
    b: float = Field(gt=0, description="Ancho de la sección")
    h: float = Field(gt=0, description="Canto total")
    d: float = Field(gt=0, description="Canto útil")
    c: float = Field(ge=0, description="Recubrimiento")
    fck: float = Field(gt=0, description="Resistencia hormigón")
    fyk: float = Field(gt=0, description="Límite elástico acero")
    ved: float = Field(ge=0, description="Cortante de cálculo")
    ned: float = Field(default=0.0, description="Axil")
    sigma_s: float = Field(gt=0, description="Tensión acero")
    As: float = Field(gt=0, description="Área armadura")
    phi_eq: float = Field(gt=0, description="Diámetro equivalente")
    asw: float = Field(ge=0, description="Área estribos")
    s: float = Field(gt=0, description="Separación estribos")
    theta: float = Field(ge=21.8, le=45.0, description="Ángulo de bielas")

def calculate_element(payload: dict) -> SolverResponse:
    """Adaptador actualizado para recibir un diccionario plano del Dispatcher."""
    
    # 1. Mapeo de compatibilidad: JSON de entrada a veces usa 'bw' en lugar de 'b'
    if "bw" in payload and "b" not in payload:
        payload["b"] = payload["bw"]
        
    # Limpiamos variables internas que Pydantic no necesita.
    payload.pop("_features", None)
    payload.pop("_form_key", None)

    # 2. Intentamos instanciar el modelo Pydantic
    try:
        inputs = InputModel(**payload)
    except ValidationError as e:
        # Si falta algo en el JSON, mostramos el error elegantemente en la UI
        missing_fields = [err["loc"][0] for err in e.errors()]
        return SolverResponse(
            is_ok=False, 
            summary=f"Faltan variables en el config.json para este adaptador: {', '.join(missing_fields)}", 
            checks=[]
        )

    # 3. CÁLCULO DE FISURACIÓN 
    res_crack, _ = crack_width(
        b=inputs.b, h=inputs.h, fck=inputs.fck, c=inputs.c, 
        sigma_s=inputs.sigma_s, As=inputs.As, phi_eq=inputs.phi_eq, 
        ds=inputs.d, Es=200000.0, load_duration='long', bond_type='bond'
    )
    wk = res_crack.get('wk', 0.0)

    # 4. CÁLCULO DE CORTANTE 
    z_eff = 0.9 * inputs.d
    res_shear, _ = shear_cheks(
        ved=inputs.ved * 1000, 
        fck=inputs.fck, fyk=inputs.fyk, asw=inputs.asw, s=inputs.s, 
        z=z_eff, theta=inputs.theta, d=inputs.d,
        asl=inputs.As, bw=inputs.b, ned=inputs.ned * 1000, 
        Ac=inputs.b * inputs.h, sismic_comb=False
    )

    # 5. EMPAQUETADO DE RESULTADOS (Ejemplo básico)
    # Aquí puedes extraer VRdc de res_shear y montar tu lista de CheckResult
    vrdc_val = res_shear.get("VRdc", 0.0) * 0.001 # Pasando a kN
    
    checks = [
        CheckResult(
            description="Agotamiento a Cortante (VRd,c)",
            status=vrdc_val >= inputs.ved,
            value=round(vrdc_val, 3),
            limit=round(inputs.ved, 3),
            unit="kN"
        ),
        CheckResult(
            description="Ancho de Fisura (wk)",
            status=wk <= 0.3, # Asumiendo un límite normativo genérico de 0.3mm
            value=round(wk, 3),
            limit=0.3,
            unit="mm"
        )
    ]

    return SolverResponse(
        is_ok=all(c.status for c in checks), 
        summary="Cálculo procesado correctamente.", 
        checks=checks
    )