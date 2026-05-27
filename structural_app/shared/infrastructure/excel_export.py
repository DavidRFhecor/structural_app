import reflex as rx
import io
import os
from typing import Dict, Any
from structural_app.core.session_io import SessionIO

# Colores corporativos FHECOR
FHECOR_BLUE     = "#003264"
FHECOR_BLUE_MID = "#B4CDE6"
FHECOR_BLUE_BG  = "#E6EEF8"
GREEN_BG        = "#C6EFCE"
GREEN_FG        = "#006100"
RED_BG          = "#FFC7CE"
RED_FG          = "#9C0006"
YELLOW_BG       = "#FFF2CC"
YELLOW_FG       = "#7D6608"
GRAY_BG         = "#F2F2F2"
WHITE           = "#FFFFFF"


class ExcelExportProvider:
    """Generador de Memorias de Cálculo en Excel con formato corporativo FHECOR."""

    @staticmethod
    def _build_formats(workbook) -> Dict[str, Any]:
        """Define todos los formatos reutilizables del libro."""
        base = {"font_name": "Calibri", "font_size": 10}

        def fmt(**kwargs):
            return workbook.add_format({**base, **kwargs})

        return {
            # Cabeceras de documento
            "doc_title": fmt(bold=True, font_size=16, font_color=FHECOR_BLUE),
            "meta_label": fmt(bold=True, bg_color=FHECOR_BLUE_BG, border=1),
            "meta_value": fmt(bg_color=FHECOR_BLUE_BG, border=1),

            # Secciones principales
            "section": fmt(bold=True, font_size=11, font_color=WHITE,
                           bg_color=FHECOR_BLUE, border=1, align="left",
                           valign="vcenter"),

            # Pestañas / agrupaciones de tab
            "tab_header": fmt(bold=True, font_color=FHECOR_BLUE,
                              bg_color=FHECOR_BLUE_MID, border=1, italic=True),

            # Grupos de campos
            "group_header": fmt(bold=True, bg_color=FHECOR_BLUE_BG, border=1),

            # Filas de datos
            "field_label": fmt(bg_color=GRAY_BG, border=1),
            "field_value": fmt(border=1, align="right", num_format="0.###"),
            "field_unit":  fmt(border=1, font_color="#666666"),

            # Estado global
            "apto":    fmt(bold=True, bg_color=GREEN_BG,  font_color=GREEN_FG,
                           border=2, align="center", valign="vcenter", font_size=12),
            "no_apto": fmt(bold=True, bg_color=RED_BG,    font_color=RED_FG,
                           border=2, align="center", valign="vcenter", font_size=12),
            "pending": fmt(bold=True, bg_color=YELLOW_BG, font_color=YELLOW_FG,
                           border=2, align="center", valign="vcenter", font_size=12),

            # Checks
            "check_header": fmt(bold=True, bg_color=FHECOR_BLUE_BG, border=1, align="center"),
            "check_desc":   fmt(border=1),
            "check_val":    fmt(border=1, align="center"),
            "cumple":       fmt(bold=True, bg_color=GREEN_BG,  font_color=GREEN_FG,
                                border=1, align="center"),
            "no_cumple":    fmt(bold=True, bg_color=RED_BG,    font_color=RED_FG,
                                border=1, align="center"),
            "ratio_ok":     fmt(border=1, align="center", bg_color=GREEN_BG,
                                font_color=GREEN_FG, num_format="0.00"),
            "ratio_fail":   fmt(border=1, align="center", bg_color=RED_BG,
                                font_color=RED_FG,  num_format="0.00"),

            # Tablas intermedias
            "table_title":  fmt(bold=True, font_color=FHECOR_BLUE, font_size=10),
            "table_col_ok": fmt(bold=True, bg_color=FHECOR_BLUE_BG, border=1,
                                font_color=FHECOR_BLUE, align="center"),
            "table_col":    fmt(bg_color=FHECOR_BLUE_BG, border=1, align="center"),
            "table_cell":   fmt(border=1, align="center"),
            "table_hi":     fmt(bold=True, border=1, align="center",
                                font_color=FHECOR_BLUE),
            "note":         fmt(italic=True, font_color="#666666", font_size=8),
        }

    # ------------------------------------------------------------------
    @staticmethod
    def _build_excel_binary(payload: Dict[str, Any]) -> bytes:
        output      = io.BytesIO()
        results     = payload.get("results", {})
        checks_list = results.get("checks", [])
        tables_list = results.get("intermediate_tables", [])
        project     = payload.get("project_info", {})
        inputs      = payload.get("inputs", [])

        has_checks    = len(checks_list) > 0
        global_is_ok  = has_checks and all(
            "CUMPLE" in str(c.get("status", "")) and "NO" not in str(c.get("status", ""))
            for c in checks_list
        )

        with io.BytesIO() as output:
            import xlsxwriter
            workbook  = xlsxwriter.Workbook(output, {"in_memory": True})
            worksheet = workbook.add_worksheet("Informe de Cálculo")
            F = ExcelExportProvider._build_formats(workbook)

            # Anchos de columna fijos
            worksheet.set_column("A:A", 42)
            worksheet.set_column("B:B", 18)
            worksheet.set_column("C:C", 12)
            worksheet.set_column("D:D", 14)
            worksheet.set_column("E:E", 10)

            r = 0  # fila actual (0-based)

            # ── TÍTULO DEL DOCUMENTO ──────────────────────────────────
            worksheet.merge_range(r, 0, r, 4,
                                  "FHECOR  ·  MEMORIA DE CÁLCULO ESTRUCTURAL",
                                  F["doc_title"])
            r += 1
            worksheet.set_row(r - 1, 26)

            # Metadatos
            for label, value in [
                ("Proyecto", project.get("title", "")),
                ("Categoría", project.get("category", "")),
                ("Fecha",    project.get("date", "")),
            ]:
                if not value:
                    continue
                worksheet.write(r, 0, label, F["meta_label"])
                worksheet.merge_range(r, 1, r, 4, value, F["meta_value"])
                r += 1

            r += 1

            # ── ESTADO GLOBAL ─────────────────────────────────────────
            worksheet.merge_range(r, 0, r, 4, "RESUMEN DE COMPROBACIÓN GLOBAL", F["section"])
            worksheet.set_row(r, 18)
            r += 1

            if not has_checks:
                status_text, status_fmt = "⏳  CÁLCULO PENDIENTE", F["pending"]
            elif global_is_ok:
                status_text, status_fmt = "✔  APTO — CUMPLE TODAS LAS COMPROBACIONES", F["apto"]
            else:
                status_text, status_fmt = "✖  NO APTO — FALLA EN ALGUNA COMPROBACIÓN", F["no_apto"]

            worksheet.merge_range(r, 0, r + 1, 4, status_text, status_fmt)
            worksheet.set_row(r, 20)
            worksheet.set_row(r + 1, 20)
            r += 3

            # ── DATOS DE ENTRADA ──────────────────────────────────────
            worksheet.merge_range(r, 0, r, 4, "1.  DATOS DE ENTRADA", F["section"])
            worksheet.set_row(r, 18)
            r += 1

            current_tab = None
            for group in inputs:
                tab = group.get("tab", "")

                # Separador de pestaña cuando cambia
                if tab and tab != current_tab:
                    current_tab = tab
                    worksheet.merge_range(r, 0, r, 4, f"  ❖  {tab}", F["tab_header"])
                    r += 1

                # Cabecera de grupo
                worksheet.merge_range(r, 0, r, 4,
                                      f"  ▸  {group.get('group', '')}", F["group_header"])
                r += 1

                for field in group.get("fields", []):
                    label = field.get("label", "")
                    value = field.get("value", "")
                    unit  = field.get("unit", "")

                    worksheet.write(r, 0, f"   {label}", F["field_label"])
                    # Intentar escribir como número para mejor formato
                    try:
                        worksheet.write_number(r, 1, float(value), F["field_value"])
                    except (ValueError, TypeError):
                        worksheet.write(r, 1, str(value), F["field_value"])
                    worksheet.write(r, 2, unit, F["field_unit"])
                    worksheet.merge_range(r, 3, r, 4, "", F["field_value"])
                    r += 1

                r += 1

            # ── COMPROBACIONES NORMATIVAS ─────────────────────────────
            worksheet.merge_range(r, 0, r, 4, "2.  COMPROBACIONES NORMATIVAS", F["section"])
            worksheet.set_row(r, 18)
            r += 1

            # Cabecera de tabla
            for col, header in enumerate(["DESCRIPCIÓN", "VALOR", "LÍMITE", "ESTADO", "RATIO"]):
                worksheet.write(r, col, header, F["check_header"])
            r += 1

            for check in checks_list:
                desc   = check.get("desc", "")
                val    = check.get("val", "")
                lim    = check.get("lim", "")
                status = str(check.get("status", ""))
                ratio  = check.get("ratio", None)

                cumple = "CUMPLE" in status and "NO" not in status
                st_fmt = F["cumple"] if cumple else F["no_cumple"]

                worksheet.write(r, 0, desc,   F["check_desc"])
                worksheet.write(r, 1, val,    F["check_val"])
                worksheet.write(r, 2, lim,    F["check_val"])
                worksheet.write(r, 3, status, st_fmt)

                if ratio is not None:
                    try:
                        ratio_f = float(ratio)
                        r_fmt = F["ratio_ok"] if ratio_f >= 1.0 else F["ratio_fail"]
                        worksheet.write_number(r, 4, ratio_f, r_fmt)
                    except (ValueError, TypeError):
                        worksheet.write(r, 4, str(ratio), F["check_val"])
                else:
                    worksheet.write(r, 4, "", F["check_val"])

                r += 1

            r += 1

            # ── TABLAS INTERMEDIAS ────────────────────────────────────
            if tables_list:
                worksheet.merge_range(r, 0, r, 4,
                                      "3.  TABLAS DE CÁLCULO INTERMEDIAS", F["section"])
                worksheet.set_row(r, 18)
                r += 1

                for table in tables_list:
                    title   = table.get("title", "")
                    note    = table.get("note", "")
                    columns = table.get("columns", [])
                    rows    = table.get("rows", [])

                    if not columns:
                        continue

                    worksheet.write(r, 0, f"  ▸  {title}", F["table_title"])
                    r += 1

                    # Cabecera de columnas
                    for ci, col in enumerate(columns):
                        label = col.get("label", "")
                        unit  = col.get("unit", "")
                        text  = f"{label} ({unit})" if unit else label
                        hi    = col.get("highlight", False)
                        worksheet.write(r, ci, text, F["table_col_ok"] if hi else F["table_col"])
                    r += 1

                    # Filas de datos
                    for row_data in rows:
                        for ci, col in enumerate(columns):
                            col_id = col.get("id", "")
                            hi     = col.get("highlight", False)
                            cell   = row_data.get(col_id, "")
                            cell_fmt = F["table_hi"] if hi else F["table_cell"]
                            try:
                                worksheet.write_number(r, ci, float(cell), cell_fmt)
                            except (ValueError, TypeError):
                                worksheet.write(r, ci, str(cell), cell_fmt)
                        r += 1

                    if note:
                        worksheet.write(r, 0, f"* {note}", F["note"])
                        r += 1

                    r += 1

            workbook.close()
            return output.getvalue()

    @staticmethod
    def save_excel_to_server(payload: Dict[str, Any], directory: str, filename: str):
        try:
            if not filename.endswith(".xlsx"):
                filename += ".xlsx"
            directory = SessionIO.resolve_path(directory)
            os.makedirs(directory, exist_ok=True)
            full_path = os.path.join(directory, filename)
            excel_bytes = ExcelExportProvider._build_excel_binary(payload)
            with open(full_path, "wb") as f:
                f.write(excel_bytes)
            return rx.toast.success(f"Informe Excel generado: {full_path}")
        except Exception as e:
            return rx.toast.error(f"Error al generar Excel: {str(e)}")