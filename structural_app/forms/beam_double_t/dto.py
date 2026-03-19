from pydantic import BaseModel, Field

class BeamDoubleTInputs(BaseModel):
    # Geometría (mm)
    h: float = Field(1200.0, ge=0)
    b_top: float = Field(600.0, ge=0)
    t_top: float = Field(150.0, ge=0)
    b_bot: float = Field(400.0, ge=0)
    t_bot: float = Field(150.0, ge=0)
    tw: float = Field(120.0, ge=0)
    
    # Materiales y Cargas
    fck: float = Field(35.0, ge=0)
    med: float = Field(500.0, help="Momento de diseño en kNm")
    ved: float = Field(200.0, help="Cortante de diseño en kN")

class BeamDoubleTResults(BaseModel):
    # Resultados mapeados del motor
    m_rd: float
    v_rd: float
    is_safe_m: bool
    is_safe_v: bool
    util_m: float
    util_v: float