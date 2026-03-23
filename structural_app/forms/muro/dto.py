from pydantic import BaseModel, Field

class MuroDTO(BaseModel):
    """Datos de entrada para el cálculo del muro (unidades en metros/kN/MPa)."""
    h_muro: float = Field(..., gt=0)
    e_superior: float = Field(..., gt=0)
    e_inferior: float = Field(..., gt=0)
    b_zapata: float = Field(..., gt=0)
    c_puntera: float = Field(..., ge=0)
    h_zapata: float = Field(..., gt=0)
    
    # Materiales y Cargas
    fck: float = 25.0
    fyk: float = 500.0
    ned: float = 0.0  # Axil en kN