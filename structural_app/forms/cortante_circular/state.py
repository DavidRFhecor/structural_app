import reflex as rx
from typing import Optional
from structural_app.core.base_state import BaseState
from structural_app.core.solver_dispatcher import SolverDispatcher
from structural_app.forms.cortante_circular.dto import CortanteCircularDTO
from structural_app.shared.domain.result_models import SolverResponse
from structural_app.shared.services.export_payloads import ExportPayloadService
from structural_app.shared.infrastructure.pdf_export import PDFExportProvider

class CortanteCircularState(BaseState):
    """Maneja los inputs, resultados y visualización del cortante circular."""
    
    # --- Inputs de Ingeniería ---
    diametro: float = 500.0
    fck: float = 30.0
    recubrimiento: float = 40.0
    as_principal: float = 1200.0
    ved: float = 150.0

    # --- Resultados ---
    results: Optional[SolverResponse] = SolverResponse(is_ok=True, checks=[], summary="Esperando cálculo...")

    # --- Lógica de Visualización (SVG) ---
    @rx.var
    def int_radius(self) -> float:
        """Calcula el radio de la armadura para el SVG."""
        ext_radius = 80.0
        if self.diametro <= 0:
            return ext_radius * 0.9
        recub_ratio = self.recubrimiento / (self.diametro / 2)
        return ext_radius * (1 - recub_ratio)

    @rx.var
    def diametro_label(self) -> str:
        """Genera el texto de la cota."""
        return f"D={self.diametro}mm"

    @rx.var
    def svg_string(self) -> str:
        """Genera el código SVG puro renderizado dinámicamente en el servidor."""
        center = 100
        ext_radius = 80
        # Inyectamos las variables matemáticas usando f-strings de Python
        return f"""
        <svg viewBox="0 0 200 200" width="100%" height="300px">
            <circle cx="{center}" cy="{center}" r="{ext_radius}" stroke="#4B5563" stroke-width="2" fill="#E5E7EB" />
            <circle cx="{center}" cy="{center}" r="{self.int_radius}" stroke="#2563EB" stroke-width="1" fill="none" stroke-dasharray="4" />
            <line x1="{center}" y1="{center}" x2="{center+ext_radius}" y2="{center}" stroke="#374151" />
            <text x="{center + 10}" y="{center - 5}" font-size="10" fill="#374151">{self.diametro_label}</text>
        </svg>
        """

    # --- Lógica de Negocio (Cálculo y Exportación) ---
    async def calculate(self):
        """Ejecuta el cálculo estructural."""
        self.is_calculating = True
        yield
        
        dto = CortanteCircularDTO(
            diametro=self.diametro,
            fck=self.fck,
            recubrimiento=self.recubrimiento,
            as_principal=self.as_principal,
            ved=self.ved
        )
        
        self.results = await SolverDispatcher.dispatch("cortante_circular", dto)
        self.is_calculating = False

    def export_pdf(self):
        """Genera y descarga el informe técnico."""
        payload = ExportPayloadService.create_report_data(
            self.active_form_config, 
            self
        )
        return PDFExportProvider.generate_calculation_report(payload)
    
    def on_load(self):
        """Este método se ejecuta al cargar la página y soluciona el error."""
        self.current_form_key = "cortante_circular"
        # Opcional: limpiar resultados previos al entrar
        # self.results = None