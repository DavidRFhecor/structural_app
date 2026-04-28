from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class CheckResult(BaseModel):
    description: str
    status: bool
    value: float
    limit: float
    unit: str
    ratio: float = 0.0

class SolverResponse(BaseModel):
    is_ok: bool
    summary: str
    checks: List[CheckResult]
    # Cambiamos a Any para que Pydantic no se queje del formato interno de Plotly
    plot_data: Optional[Any] = None