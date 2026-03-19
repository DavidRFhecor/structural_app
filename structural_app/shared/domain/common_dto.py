from pydantic import BaseModel, Field
from typing import Optional

class ProjectMetadataDTO(BaseModel):
    """Información general del proyecto para cajetines y reportes."""
    project_name: str = "Nuevo Proyecto"
    project_id: str = "0000"
    author: str = "Ingeniero FHECOR"
    client: Optional[str] = None

class MaterialPropertiesDTO(BaseModel):
    """Propiedades mecánicas base."""
    fck: float = Field(30.0, description="Resistencia característica a compresión (MPa)")
    fyk: float = Field(500.0, description="Límite elástico del acero (MPa)")
    gamma_c: float = 1.5
    gamma_s: float = 1.15