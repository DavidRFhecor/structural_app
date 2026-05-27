from __future__ import annotations
import reflex as rx
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from plotly.graph_objs import Figure
from typing import List, Optional, Dict, Any

class CheckResult(BaseModel):
    description: str = ""
    status: bool = True
    value: float = 0.0
    limit: float = 0.0
    unit: str = ""
    ratio: float = 0.0
    reference: str = ""


class TableColumn(BaseModel):
    id: str
    label: str
    unit: str = ""
    highlight: bool = False
    format: str = ".3f"


class IntermediateTable(BaseModel):
    id: str
    title: str
    columns: List[TableColumn] = []
    rows: List[Dict[str, Any]] = []
    footer: Optional[Dict[str, Any]] = None
    note: str = ""


class ScenarioResult(BaseModel): 
    label: str
    checks: List[CheckResult] = []
    is_ok: bool = True

class DerivedValue(BaseModel):
    label: str
    value: float
    unit: str = ""
    formula: str = ""


class MaterialResult(BaseModel):
    items: List[DerivedValue] = []


class MeasurementLine(BaseModel):
    description: str
    quantity: float
    unit: str
    unit_price: float = 0.0
    total: float = 0.0


class MeasurementResult(BaseModel):
    lines: List[MeasurementLine] = []
    grand_total: float = 0.0
    currency: str = "€"


class SolverResponse(BaseModel):
    is_ok: bool = True
    summary: str = ""
    checks: List[CheckResult] = []
    plot_data: Optional[Dict[str, Any]] = None
    form_data_updates: Optional[Dict[str, Any]] = None
    warnings: List[str] = []
    material_results: Optional[MaterialResult] = None
    scenarios: Dict[str, ScenarioResult] = {}
    intermediate_tables: List[IntermediateTable] = []
    measurements: Optional[MeasurementResult] = None