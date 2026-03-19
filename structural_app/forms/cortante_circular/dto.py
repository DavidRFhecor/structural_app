from pydantic import BaseModel, Field

class CortanteCircularDTO(BaseModel):
    """Objeto de transferencia de datos para el cálculo de cortante."""
    diametro: float = Field(..., gt=0)
    fck: float = Field(..., ge=12)
    recubrimiento: float = Field(..., ge=20)
    as_principal: float = Field(..., gt=0)
    ved: float = Field(..., ge=0)