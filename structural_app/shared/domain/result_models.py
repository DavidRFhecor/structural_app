from pydantic import BaseModel
from typing import List, Optional

class CheckResult(BaseModel):
    description: str = ""
    status: bool = True
    value: float = 0.0
    limit: float = 0.0
    unit: str = ""
    ratio: float = 0.0
    reference: str = ""

class SolverResponse(BaseModel):
    is_ok: bool = True
    summary: str = ""
    checks: List[CheckResult] = [] # Tipado explícito para que foreach funcione
    metadata: Optional[dict] = None