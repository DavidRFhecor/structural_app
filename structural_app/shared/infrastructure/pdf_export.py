import os
import reflex as rx
from fpdf import FPDF
from typing import Dict, Any
from structural_app.core.session_io import SessionIO

class PDFReport(FPDF):
    """Estilo visual corporativo FHECOR."""
    def header(self):
        # Asegúrate de usar 'Lato' en lugar de 'Arial'
        self.set_font('Lato', 'B', 12) 
        self.set_text_color(0, 50, 100) # Azul FHECOR
        self.cell(0, 10, 'FHECOR - MEMORIA DE CÁLCULO ESTRUCTURAL', 0, 1, 'C')
        self.set_draw_color(0, 50, 100)
        self.line(10, 20, 200, 20)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Lato', '', 8) 
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Página {self.page_no()} | Generado por Structural Hub', 0, 0, 'C')

class PDFExportProvider:
    @staticmethod
    def _build_pdf_binary(payload: Dict[str, Any]) -> bytes:
        pdf = PDFReport()
        
        # --- NUEVO: REGISTRO DE FUENTES LATO ---
        # ATENCIÓN: Asegúrate de que los nombres de los archivos coincidan 
        # exactamente con los que tienes en tu carpeta assets.
        pdf.add_font('Lato', '', 'assets/Lato-Regular.ttf', uni=True)
        pdf.add_font('Lato', 'B', 'assets/Lato-Bold.ttf', uni=True)
        # Si tienes la cursiva, añádela así: pdf.add_font('Lato', 'I', 'assets/Lato-Italic.ttf', uni=True)

        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        project = payload.get('project_info', {})
        results = payload.get('results', {})
        checks = results.get('checks', [])
        has_checks = len(checks) > 0
        is_ok = results.get('is_ok', False) and has_checks

        # 1. IDENTIFICACIÓN
        pdf.set_font('Lato', 'B', 14) # Cambiado a Lato
        pdf.cell(0, 10, str(project.get('title', 'Informe')).upper(), 0, 1, 'L')
        pdf.set_font('Lato', '', 10) # Cambiado a Lato
        pdf.cell(0, 7, f"Fecha: {project.get('date', '')}", 0, 1, 'L')
        pdf.ln(5)

        # 2. ESTADO GLOBAL
        pdf.set_font('Lato', 'B', 11) # Cambiado a Lato
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 10, ' RESUMEN DE ESTADO', 1, 1, 'L', fill=True)
        
        if not has_checks:
            pdf.set_fill_color(255, 242, 204) 
            pdf.set_text_color(147, 137, 83)
            status_text = "CÁLCULO PENDIENTE"
        elif is_ok:
            pdf.set_fill_color(200, 240, 200) 
            pdf.set_text_color(0, 80, 0)
            status_text = "APTO / CUMPLE TODAS LAS COMPROBACIONES"
        else:
            pdf.set_fill_color(255, 200, 200) 
            pdf.set_text_color(120, 0, 0)
            status_text = "NO APTO / FALLA EN COMPROBACIONES"
        
        pdf.set_font('Lato', 'B', 12) # Cambiado a Lato
        pdf.cell(0, 12, status_text, 1, 1, 'C', fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

        # 3. INPUTS 
        pdf.set_font('Lato', 'B', 11) # Cambiado a Lato
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 10, ' 1. DATOS DE ENTRADA', 1, 1, 'L', fill=True)
        for group in payload.get('inputs', []):
            pdf.ln(2)
            pdf.set_font('Lato', 'B', 10) # Cambiado a Lato
            pdf.set_text_color(0, 50, 100) # Azul FHECOR aplicado
            pdf.cell(0, 8, f"  > {group['group']}", 0, 1, 'L')
            pdf.set_font('Lato', '', 10) # Cambiado a Lato
            pdf.set_text_color(0, 0, 0)
            for f in group.get('fields', []):
                pdf.cell(100, 6, f"     {f['label']}", 0, 0, 'L')
                pdf.cell(40, 6, f"{f['value']} {f['unit']}", 0, 1, 'R')
        pdf.ln(5)

        # 4. CHECKS 
        pdf.set_font('Lato', 'B', 11) # Cambiado a Lato
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 10, ' 2. COMPROBACIONES NORMATIVAS', 1, 1, 'L', fill=True)
        pdf.ln(2)
        pdf.set_font('Lato', 'B', 9) # Cambiado a Lato
        pdf.cell(85, 10, ' DESCRIPCIÓN', 1, 0, 'C', fill=True)
        pdf.cell(35, 10, ' VALOR', 1, 0, 'C', fill=True)
        pdf.cell(35, 10, ' LÍMITE', 1, 0, 'C', fill=True)
        pdf.cell(35, 10, ' ESTADO', 1, 1, 'C', fill=True)

        pdf.set_font('Lato', '', 9) # Cambiado a Lato
        for c in checks:
            pdf.cell(85, 10, f" {c['desc']}", 1)
            pdf.cell(35, 10, c['val'], 1, 0, 'C')
            pdf.cell(35, 10, c['lim'], 1, 0, 'C')
            st = str(c['status'])
            is_c = "CUMPLE" in st and "NO" not in st
            pdf.set_text_color(0, 128, 0) if is_c else pdf.set_text_color(200, 0, 0)
            pdf.cell(35, 10, st, 1, 1, 'C')
            pdf.set_text_color(0, 0, 0)

        return bytes(pdf.output())

    @staticmethod
    def save_pdf_to_server(payload: Dict[str, Any], directory: str, filename: str):
        try:
            if not filename.endswith(".pdf"): filename += ".pdf"
            directory = SessionIO.resolve_path(directory) 
            os.makedirs(directory, exist_ok=True)
            full_path = os.path.join(directory, filename)
            pdf_bytes = PDFExportProvider._build_pdf_binary(payload)
            with open(full_path, 'wb') as f: f.write(pdf_bytes) 
            return rx.toast.success(f"PDF generado: {full_path}")
        except Exception as e:
            return rx.toast.error(f"Error PDF: {str(e)}")