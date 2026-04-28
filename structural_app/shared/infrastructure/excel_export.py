import reflex as rx
import pandas as pd
import io
import os
from structural_app.core.session_io import SessionIO

class ExcelExportProvider:
    """Generador de Memorias de Cálculo en Excel con formato corporativo y estados inteligentes."""

    @staticmethod
    def _build_excel_binary(payload: dict) -> bytes:
        """Diseña un informe técnico estructurado con lógica de validación de cálculo."""
        output = io.BytesIO()
        results = payload.get("results", {})
        checks_list = results.get("checks", [])
        project_info = payload.get("project_info", {})

        # Lógica de estados: PENDIENTE si no hay checks, de lo contrario APTO/NO APTO
        has_checks = len(checks_list) > 0
        global_is_ok = all(
            "CUMPLE" in str(c.get("status", "")) and "NO" not in str(c.get("status", "")) 
            for c in checks_list
        ) if has_checks else False

        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook = writer.book
            worksheet = workbook.add_worksheet('Informe de Cálculo')
            
            # --- DEFINICIÓN DE ESTILOS ---
            title_fmt = workbook.add_format({'font_name': 'Lato', 'bold': True, 'font_size': 18, 'font_color': '#003264'})
            header_fmt = workbook.add_format({'font_name': 'Lato', 'bold': True, 'bg_color': '#E7E6E6', 'border': 1, 'font_size': 12})
            label_fmt = workbook.add_format({'font_name': 'Lato', 'bold': True, 'font_size': 10, 'bg_color': '#F8F9FA', 'border': 1})
            val_fmt = workbook.add_format({'font_name': 'Lato', 'border': 1, 'align': 'right', 'font_size': 10})
            
            apto_fmt = workbook.add_format({'font_name': 'Lato', 'bold': True, 'bg_color': '#C6EFCE', 'font_color': '#006100', 'border': 2, 'align': 'center'})
            no_apto_fmt = workbook.add_format({'font_name': 'Lato', 'bold': True, 'bg_color': '#FFC7CE', 'font_color': '#9C0006', 'border': 2, 'align': 'center'})
            pending_fmt = workbook.add_format({'font_name': 'Lato', 'bold': True, 'bg_color': '#FFF2CC', 'font_color': '#938953', 'border': 2, 'align': 'center'})

            # 1. ENCABEZADO
            worksheet.merge_range('A1:E1', "FHECOR | MEMORIA DE CÁLCULO ESTRUCTURAL", title_fmt)
            worksheet.write('A3', 'PROYECTO:', label_fmt)
            worksheet.merge_range('B3:E3', str(project_info.get("title", "")), val_fmt)
            worksheet.write('A4', 'FECHA:', label_fmt)
            worksheet.merge_range('B4:E4', str(project_info.get("date", "")), val_fmt)

            # 2. RESUMEN GLOBAL 
            worksheet.merge_range('A6:E6', "RESUMEN DE COMPROBACIÓN GLOBAL", header_fmt)
            
            if not has_checks:
                status_text, current_fmt = "CÁLCULO PENDIENTE", pending_fmt
            else:
                status_text = "ESTADO: APTO / CUMPLE" if global_is_ok else "ESTADO: NO APTO / FALLA"
                current_fmt = apto_fmt if global_is_ok else no_apto_fmt
            
            worksheet.merge_range('A7:E8', status_text, current_fmt)

            # 3. DATOS DE ENTRADA
            curr_row = 10
            worksheet.merge_range(f'A{curr_row}:E{curr_row}', "1. PARÁMETROS DE DISEÑO (INPUTS)", header_fmt)
            curr_row += 1
            for group in payload.get("inputs", []):
                worksheet.merge_range(f'A{curr_row}:E{curr_row}', f"   > {group['group']}", label_fmt)
                curr_row += 1
                for f in group.get('fields', []):
                    worksheet.write(curr_row, 0, f.get('label', ''), label_fmt)
                    worksheet.write(curr_row, 1, f.get('value', 0.0), val_fmt)
                    worksheet.write(curr_row, 2, f.get('unit', ''), val_fmt)
                    curr_row += 1
                curr_row += 1

            # 4. COMPROBACIONES DETALLADAS
            worksheet.merge_range(f'A{curr_row}:E{curr_row}', "2. COMPROBACIONES NORMATIVAS", header_fmt)
            curr_row += 1
            for i, h in enumerate(["DESCRIPCIÓN", "VALOR", "LÍMITE", "ESTADO"]):
                worksheet.write(curr_row, i, h, label_fmt)
            
            curr_row += 1
            for check in checks_list:
                worksheet.write(curr_row, 0, check.get("desc", ""), val_fmt)
                worksheet.write(curr_row, 1, check.get("val", ""), val_fmt)
                worksheet.write(curr_row, 2, check.get("lim", ""), val_fmt)
                st = str(check.get("status", ""))
                is_ok = "CUMPLE" in st and "NO" not in st
                worksheet.write(curr_row, 3, st, apto_fmt if is_ok else no_apto_fmt)
                curr_row += 1

            worksheet.set_column('A:A', 45)
            worksheet.set_column('B:E', 18)

        return output.getvalue()

    @staticmethod
    def save_excel_to_server(payload: dict, directory: str, filename: str):
        try:
            if not filename.endswith(".xlsx"): filename += ".xlsx"
            directory = SessionIO.resolve_path(directory) #
            os.makedirs(directory, exist_ok=True)
            full_path = os.path.join(directory, filename)
            excel_bytes = ExcelExportProvider._build_excel_binary(payload)
            with open(full_path, 'wb') as f: f.write(excel_bytes) #
            return rx.toast.success(f"Informe Excel generado: {full_path}")
        except Exception as e:
            return rx.toast.error(f"Error al generar Excel: {str(e)}")