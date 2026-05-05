from __future__ import annotations
import reflex as rx
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from plotly.graph_objs import Figure

class CheckResult(rx.Base): 
    description: str
    status: bool
    value: float
    limit: float
    unit: str
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


class ScenarioResult(rx.Base): 
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


class SolverResponse(rx.Base): 
    is_ok: bool = True
    summary: str = ""
    checks: List[CheckResult] = []
    scenarios: Dict[str, ScenarioResult] = {} 
    intermediate_tables: List[IntermediateTable] = []
    material_results: MaterialResult = MaterialResult()
    measurements: MeasurementResult = MeasurementResult()
    warnings: List[str] = []
    plot_data: Optional[Figure] = None