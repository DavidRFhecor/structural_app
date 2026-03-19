from pydantic import BaseModel, Field
from ....shared.domain.common_dto import MaterialPropertiesDTO

class ElementDTO(BaseModel):
    """Estructura de datos para [Nombre del Elemento]."""
    # Inputs Geométricos
    ancho: float = Field(..., gt=0)
    canto: float = Field(..., gt=0)
    
    # Materiales (Reutilizando DTO común)
    materiales: MaterialPropertiesDTO = MaterialPropertiesDTO()
    
    # Esfuerzos
    n_ed: float = Field(0.0, description="Axil de cálculo")