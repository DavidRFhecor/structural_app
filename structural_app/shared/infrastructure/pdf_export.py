import os
import reflex as rx
from fpdf import FPDF
from typing import Dict, Any, List
from structural_app.core.session_io import SessionIO

# ---------------------------------------------------------------------------
# Constantes de diseño FHECOR
# ---------------------------------------------------------------------------
FHECOR_BLUE       = (0, 50, 100)
FHECOR_BLUE_LIGHT = (230, 238, 248)
FHECOR_BLUE_MID   = (180, 205, 230)
GREEN             = (0, 120, 60)
GREEN_BG          = (220, 245, 230)
RED               = (160, 0, 0)
RED_BG            = (255, 220, 220)
YELLOW_BG         = (255, 245, 200)
YELLOW_FG         = (130, 100, 0)
GRAY_LINE         = (200, 210, 220)
GRAY_TEXT         = (100, 100, 100)
WHITE             = (255, 255, 255)
BLACK             = (20, 20, 20)


# ---------------------------------------------------------------------------
# Clase base con cabecera / pie corporativo
# ---------------------------------------------------------------------------
class FHECORReport(FPDF):

    def __init__(self, title: str = "Memoria de Cálculo"):
        super().__init__()
        self._doc_title = title

    # ---- Fuentes ----
    def _load_fonts(self):
        self.add_font("Lato", "",  "assets/Lato-Regular.ttf", uni=True)
        self.add_font("Lato", "B", "assets/Lato-Bold.ttf",    uni=True)
        self.add_font("Lato", "I", "assets/Lato-Italic.ttf",  uni=True)

    # ---- Helpers de color ----
    def _set_fill(self, rgb: tuple):
        self.set_fill_color(*rgb)

    def _set_text(self, rgb: tuple):
        self.set_text_color(*rgb)

    def _set_draw(self, rgb: tuple):
        self.set_draw_color(*rgb)

    # ---- Cabecera ----
    def header(self):
        # Franja azul superior
        self._set_fill(FHECOR_BLUE)
        self.rect(0, 0, 210, 14, "F")
        self.set_font("Lato", "B", 10)
        self._set_text(WHITE)
        self.set_y(3)
        self.cell(0, 8, "FHECOR  ·  MEMORIA DE CÁLCULO ESTRUCTURAL", align="C")
        self._set_text(BLACK)
        self.ln(12)

    # ---- Pie ----
    def footer(self):
        self.set_y(-12)
        self._set_draw(FHECOR_BLUE)
        self.set_line_width(0.4)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(1)
        self.set_font("Lato", "", 7)
        self._set_text(GRAY_TEXT)
        self.cell(0, 6,
                  f"Pág. {self.page_no()}  |  Generado por Structural Hub  |  FHECOR Ingenieros",
                  align="C")
        self._set_text(BLACK)

    # ---- Título de sección ----
    def section_title(self, text: str):
        self.ln(4)
        self._set_fill(FHECOR_BLUE)
        self._set_text(WHITE)
        self.set_font("Lato", "B", 10)
        self.cell(0, 9, f"  {text}", ln=True, fill=True)
        self._set_text(BLACK)
        self.ln(2)

    # ---- Subtítulo de grupo ----
    def group_title(self, text: str):
        self._set_fill(FHECOR_BLUE_LIGHT)
        self._set_text(FHECOR_BLUE)
        self.set_font("Lato", "B", 9)
        self.cell(0, 7, f"   {text}", ln=True, fill=True)
        self._set_text(BLACK)

    # ---- Línea separadora ----
    def thin_line(self):
        self._set_draw(GRAY_LINE)
        self.set_line_width(0.2)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)


# ---------------------------------------------------------------------------
# Secciones del informe
# ---------------------------------------------------------------------------

def _build_cover(pdf: FHECORReport, project: dict, is_ok: bool, has_checks: bool):
    """Portada simple: título, fecha y estado global."""
    # Espacio de respiro tras la cabecera
    pdf.ln(12)

    # Título del cálculo
    pdf.set_font("Lato", "B", 20)
    pdf._set_text(FHECOR_BLUE)
    pdf.multi_cell(0, 10, project.get("title", "Informe de Cálculo").upper(), align="C")
    pdf._set_text(BLACK)
    pdf.ln(4)

    # Categoría (si existe)
    category = project.get("category", "")
    if category:
        pdf.set_font("Lato", "I", 11)
        pdf._set_text(GRAY_TEXT)
        pdf.cell(0, 7, category, align="C", ln=True)
        pdf._set_text(BLACK)

    pdf.ln(6)
    pdf.thin_line()
    pdf.ln(4)

    # Fecha
    pdf.set_font("Lato", "", 10)
    pdf._set_text(GRAY_TEXT)
    pdf.cell(0, 7, f"Fecha de generación:  {project.get('date', '')}", align="C", ln=True)
    pdf._set_text(BLACK)
    pdf.ln(8)

    # Pastilla de estado global
    if not has_checks:
        bg, fg, label = YELLOW_BG, YELLOW_FG, "⏳  CÁLCULO PENDIENTE"
    elif is_ok:
        bg, fg, label = GREEN_BG, GREEN, "✔  APTO — CUMPLE TODAS LAS COMPROBACIONES"
    else:
        bg, fg, label = RED_BG, RED, "✖  NO APTO — FALLA EN ALGUNA COMPROBACIÓN"

    pdf._set_fill(bg)
    pdf._set_text(fg)
    pdf.set_font("Lato", "B", 12)
    pdf.cell(0, 14, label, border=1, align="C", ln=True, fill=True)
    pdf._set_text(BLACK)
    pdf.ln(10)
    pdf.thin_line()


def _build_inputs(pdf: FHECORReport, inputs: list):
    """Sección 1 – Datos de entrada."""
    pdf.section_title("1.  DATOS DE ENTRADA")

    COL_LABEL = 120
    COL_VALUE = 60

    for group in inputs:
        pdf.group_title(group.get("group", ""))
        pdf.set_font("Lato", "", 9)
        pdf._set_text(BLACK)

        for f in group.get("fields", []):
            label = f.get("label", "")
            value = f.get("value", "")
            unit  = f.get("unit", "")
            text_value = f"{value}  {unit}".strip()

            # Alternar fondo de fila para legibilidad
            y_before = pdf.get_y()
            pdf._set_fill((248, 250, 253))
            pdf.cell(COL_LABEL, 6, f"   {label}", border="B", fill=True)
            pdf.set_font("Lato", "B", 9)
            pdf.cell(COL_VALUE, 6, text_value, border="B", align="R", ln=True)
            pdf.set_font("Lato", "", 9)

        pdf.ln(3)


def _build_checks(pdf: FHECORReport, checks: list):
    """Sección 2 – Comprobaciones normativas como tarjetas con barra de ratio."""
    pdf.section_title("2.  COMPROBACIONES NORMATIVAS")

    PAGE_W = 190   # ancho útil
    CARD_H = 18    # alto de cada tarjeta

    for c in checks:
        desc   = c.get("desc", "")
        val    = c.get("val", "")
        lim    = c.get("lim", "")
        status = str(c.get("status", ""))
        ratio_raw = c.get("ratio", None)

        # Estado y colores
        cumple = "CUMPLE" in status and "NO" not in status
        badge_bg  = GREEN    if cumple else RED
        badge_txt = "CUMPLE" if cumple else "NO CUMPLE"

        # ---- Fondo de tarjeta ----
        pdf._set_fill((245, 248, 252))
        pdf._set_draw(FHECOR_BLUE_MID)
        pdf.set_line_width(0.3)
        x0, y0 = pdf.get_x(), pdf.get_y()
        pdf.rect(x0, y0, PAGE_W, CARD_H)

        # Descripción
        pdf.set_font("Lato", "B", 9)
        pdf._set_text(FHECOR_BLUE)
        pdf.cell(110, 6, f"  {desc}", ln=False)

        # Valor / Límite
        pdf.set_font("Lato", "", 9)
        pdf._set_text(BLACK)
        pdf.cell(30, 6, f"{val}", align="C", ln=False)
        pdf.cell(20, 6, f"/ {lim}", align="C", ln=False)

        # Badge CUMPLE / NO CUMPLE
        pdf._set_fill(badge_bg)
        pdf._set_text(WHITE)
        pdf.set_font("Lato", "B", 8)
        pdf.cell(30, 6, badge_txt, align="C", ln=True, fill=True)
        pdf._set_text(BLACK)
        pdf._set_fill(WHITE)

        # ---- Barra de ratio ----
        if ratio_raw is not None:
            try:
                ratio = float(ratio_raw)
            except (ValueError, TypeError):
                ratio = 0.0

            BAR_X     = x0 + 2
            BAR_Y     = y0 + 8
            BAR_TOTAL = PAGE_W - 4
            BAR_H     = 4
            filled    = min(ratio, 1.0) * BAR_TOTAL

            # Fondo gris
            pdf._set_fill((220, 225, 230))
            pdf._set_draw((220, 225, 230))
            pdf.rect(BAR_X, BAR_Y, BAR_TOTAL, BAR_H, "F")

            # Relleno coloreado
            bar_color = GREEN if ratio >= 1.0 else RED
            pdf._set_fill(bar_color)
            if filled > 0:
                pdf.rect(BAR_X, BAR_Y, filled, BAR_H, "F")

            # Etiqueta de ratio
            pdf.set_font("Lato", "", 7)
            pdf._set_text(GRAY_TEXT)
            pdf.set_xy(BAR_X + BAR_TOTAL + 1, BAR_Y - 1)
            pdf.cell(0, BAR_H + 1, f"{ratio:.2f}", ln=False)
            pdf._set_text(BLACK)

            # Ajustar posición Y tras la barra
            pdf.set_xy(x0, y0 + CARD_H)
        else:
            pdf.set_xy(x0, y0 + CARD_H - 6)  # sin barra, tarjeta más corta

        pdf.ln(2)  # espacio entre tarjetas


def _build_intermediate_tables(pdf: FHECORReport, tables: list):
    """Sección 3 – Tablas intermedias."""
    if not tables:
        return

    pdf.section_title("3.  TABLAS DE CÁLCULO INTERMEDIAS")

    for table in tables:
        title   = table.get("title", "")
        note    = table.get("note", "")
        columns = table.get("columns", [])
        rows    = table.get("rows", [])

        if not columns:
            continue

        # Título de tabla
        pdf.set_font("Lato", "B", 9)
        pdf._set_text(FHECOR_BLUE)
        pdf.cell(0, 7, f"  ▸  {title}", ln=True)
        pdf._set_text(BLACK)

        # Cabecera de tabla
        col_w = 190 // max(len(columns), 1)
        pdf._set_fill(FHECOR_BLUE)
        pdf._set_text(WHITE)
        pdf.set_font("Lato", "B", 8)
        for col in columns:
            label = col.get("label", "")
            unit  = col.get("unit", "")
            header_text = f"{label} ({unit})" if unit else label
            pdf.cell(col_w, 7, header_text, border=1, align="C", fill=True)
        pdf.ln()
        pdf._set_text(BLACK)

        # Filas
        pdf.set_font("Lato", "", 8)
        for i, row in enumerate(rows):
            fill_row = i % 2 == 0
            pdf._set_fill((245, 248, 252) if fill_row else WHITE)
            for col in columns:
                col_id = col.get("id", "")
                cell_val = str(row.get(col_id, ""))
                is_highlight = col.get("highlight", False)
                if is_highlight:
                    pdf.set_font("Lato", "B", 8)
                    pdf._set_text(FHECOR_BLUE)
                pdf.cell(col_w, 6, cell_val, border="B", align="C", fill=fill_row)
                if is_highlight:
                    pdf.set_font("Lato", "", 8)
                    pdf._set_text(BLACK)
            pdf.ln()

        # Nota al pie de tabla
        if note:
            pdf.set_font("Lato", "I", 7)
            pdf._set_text(GRAY_TEXT)
            pdf.cell(0, 5, f"  * {note}", ln=True)
            pdf._set_text(BLACK)

        pdf.ln(4)


# ---------------------------------------------------------------------------
# Punto de entrada público
# ---------------------------------------------------------------------------
class PDFExportProvider:

    @staticmethod
    def _build_pdf_binary(payload: Dict[str, Any]) -> bytes:
        project = payload.get("project_info", {})
        results = payload.get("results", {})
        checks  = results.get("checks", [])
        tables  = results.get("intermediate_tables", [])

        has_checks = len(checks) > 0
        is_ok      = results.get("is_ok", False) and has_checks

        # --- Instanciar y configurar ---
        pdf = FHECORReport(title=project.get("title", "Informe"))
        pdf._load_fonts()
        pdf.set_auto_page_break(auto=True, margin=18)
        pdf.set_margins(10, 16, 10)
        pdf.add_page()

        # --- Secciones ---
        _build_cover(pdf, project, is_ok, has_checks)
        _build_inputs(pdf, payload.get("inputs", []))
        pdf.add_page()
        _build_checks(pdf, checks)
        _build_intermediate_tables(pdf, tables)

        return bytes(pdf.output())

    @staticmethod
    def save_pdf_to_server(payload: Dict[str, Any], directory: str, filename: str):
        try:
            if not filename.endswith(".pdf"):
                filename += ".pdf"
            directory = SessionIO.resolve_path(directory)
            os.makedirs(directory, exist_ok=True)
            full_path = os.path.join(directory, filename)
            pdf_bytes = PDFExportProvider._build_pdf_binary(payload)
            with open(full_path, "wb") as f:
                f.write(pdf_bytes)
            return rx.toast.success(f"PDF generado: {full_path}")
        except Exception as e:
            return rx.toast.error(f"Error PDF: {str(e)}")