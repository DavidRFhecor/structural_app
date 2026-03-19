from loguru import logger
from structural_app.forms.beam_double_t.dto import BeamDoubleTInputs

# Atamos el log al contexto del formulario
log = logger.bind(form_key="beam_double_t")

def run_solver(data: dict) -> dict:
    """
    Única frontera con el motor externo fhecor_structuralcodes.
    Transforma DTOs a llamadas del motor y normaliza la salida.
    """
    try:
        inputs = BeamDoubleTInputs(**data)
        
        # Simulación de llamada al motor externo
        # res = fhecor_structuralcodes.checks_ec2_2004.calc_double_t(...)
        
        m_rd_calc = (inputs.fck * inputs.h * inputs.b_top * 0.12) / 1e6 
        v_rd_calc = (inputs.tw * inputs.h * 0.18) / 1000
        
        return {
            "success": True,
            "scalars": {
                "m_rd": round(m_rd_calc, 2),
                "v_rd": round(v_rd_calc, 2),
                "util_m": round(inputs.med / m_rd_calc, 3) if m_rd_calc > 0 else 0,
                "util_v": round(inputs.ved / v_rd_calc, 3) if v_rd_calc > 0 else 0,
            },
            "meta": {"solver": "EC2_Engine_v1", "code": "EN1992-1-1"}
        }
    except Exception as e:
        log.error(f"Error en ejecución de solver: {str(e)}")
        return {"success": False, "meta": {"error": str(e)}}