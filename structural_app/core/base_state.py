import reflex as rx
import plotly.graph_objects as go
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from structural_app.core.form_registry import FORM_REGISTRY
from structural_app.core.session_io import SessionIO
from structural_app.core.solver_dispatcher import SolverDispatcher
from structural_app.shared.domain.result_models import SolverResponse
from structural_app.shared.services.export_payloads import ExportPayloadService
from structural_app.shared.infrastructure.pdf_export import PDFExportProvider


# ---------------------------------------------------------------------------
# Modelos auxiliares — FormConfig AMPLIADO con tabs y has_tabs
# ---------------------------------------------------------------------------

class BookReference(BaseModel):
    title: str = ""
    url: str = ""
class SearchResult(BaseModel):
    title: str = ""
    description: str = ""
    form_key: str = ""
class FormField(BaseModel):
    id: str = ""
    symbol: str = ""  # Agregado para el renderizador
    label: str = ""
    unit: str = ""
    type: str = "number"
    default: Any = 0.0
    options: List[Dict[str, Any]] = []
    help_text: str = ""
class FormElement(BaseModel):
    """Representa tanto un grupo de campos como una tabla."""
    type: str = "group"
    name: str = ""
    fields: List[FormField] = []
    # Campos específicos para data_table
    id: str = ""
    title: str = ""
    columns: List[Dict[str, Any]] = []
    default_rows: List[List[Any]] = []

class FormTab(BaseModel):
    id: str = ""
    label: str = ""
    groups: List[FormElement] = [] # Ahora Reflex sabe qué hay dentro

class FormConfig(BaseModel):
    form_key: str = ""
    title: str = ""
    description: str = ""
    extended_info: Optional[str] = None
    references: List[BookReference] = []
    groups: List[FormElement] = [] # Consistencia con tabs
    tabs: List[FormTab] = []
    has_tabs: bool = False
    features: Dict[str, bool] = {"svg": False, "viewer_3d": False, "sketch": False}


# ---------------------------------------------------------------------------
# Estado Base
# ---------------------------------------------------------------------------
class BaseState(rx.State):
    current_form_key: str = ""
    is_calculating: bool = False
    last_calculation_hash: str = ""
    search_query: str = ""
    form_data: Dict[str, Any] = {}
    results: SolverResponse = SolverResponse(is_ok=True, checks=[], summary="Esperando datos...")
    show_theory_popup: bool = False

    # Gestión de Archivos de Sesión (JSON)
    save_filename: str = "proyecto_calculo.json"
    save_path: str = "./"
    is_save_dialog_open: bool = False
    is_load_dialog_open: bool = False

    # Gestión de Informes (PDF)
    pdf_filename: str = "informe_calculo.pdf"
    is_pdf_dialog_open: bool = False

    # Gestión de Informes (Excel)
    excel_filename: str = "reporte_calculo.xlsx"
    is_excel_dialog_open: bool = False


    def toggle_theory(self):
        self.show_theory_popup = not self.show_theory_popup

    @rx.var
    def current_theory_content(self) -> str:
        """Retorna el contenido de teoría asegurando siempre un string."""
        if not self.active_form_config:
            return ""
        
        # Usamos getattr por seguridad y nos aseguramos de devolver str
        content = getattr(self.active_form_config, "extended_info", "")
        return content if content is not None else ""
        
    @rx.var
    def plot_fig(self) -> go.Figure:
        if self.results and self.results.plot_data:
            return go.Figure(self.results.plot_data)
        fig = go.Figure()
        fig.update_layout(title="Sin datos gráficos")
        return fig

    # -----------------------------------------------------------------------
    # set_current_form — soporta tabs (nueva) y groups (legacy)
    # -----------------------------------------------------------------------
    @rx.event
    async def set_current_form(self, key: str):
        self.current_form_key = ""
        self.results = SolverResponse(is_ok=False, checks=[], summary="Cargando...", plot_data=None)
        self.form_data = {}
        self.last_calculation_hash = ""
        yield

        self.current_form_key = key
        config = FORM_REGISTRY.get(key, {})
        new_data = {}

        # Determinar fuente de grupos: tabs o legacy
        if "tabs" in config:
            sources = [g for tab in config["tabs"] for g in tab.get("groups", [])]
        else:
            sources = config.get("groups", [])

        for element in sources:
            elem_type = element.get("type", "")

            if elem_type == "data_table":
                table_id = element.get("id") or element.get("name")
                if not table_id:
                    continue
                new_data[table_id] = element.get("default_rows", [])

            else:
                for f in element.get("fields", []):
                    field_id = f.get("id") or f.get("name")
                    if not field_id:
                        continue
                    field_type = f.get("type", "number")

                    if field_type in ("number", ""):
                        raw = f.get("default", 0.0)
                        try:
                            new_data[field_id] = float(raw)
                        except (TypeError, ValueError):
                            new_data[field_id] = 0.0

                    elif field_type == "select":
                        new_data[field_id] = f.get("default", "")

                    elif field_type == "toggle":
                        new_data[field_id] = bool(f.get("default", False))

                    elif field_type == "derived":
                        pass  # calculado por el adaptador, no se inicializa

        self.form_data = new_data
        yield

    @rx.event
    def update_table_cell(self, table_id: str, pos: tuple[int, int], value: str):
        row, col = pos
        try:
            self.form_data[table_id][row][col] = float(value)
        except ValueError:
            pass

    @rx.event
    def set_value(self, field: str, value: str):
        try:
            val = value.strip()
            self.form_data[field] = 0.0 if val in ["", "-", "."] else float(val.replace(",", "."))
        except:
            pass

    @rx.event
    def set_select_value(self, field: str, value: str):
        self.form_data[field] = value

    @rx.event
    def set_toggle_value(self, field: str, value: bool):
        self.form_data[field] = value

    @rx.event
    async def calculate(self):
        from structural_app.shared.services.hash_service import HashService

        current_hash = HashService.compute_hash(self.form_data)
        if current_hash == self.last_calculation_hash:
            return

        self.is_calculating = True
        yield

        self.last_calculation_hash = current_hash
        payload = self.form_data.copy()
        payload["_features"] = self.active_form_config.features
        self.results = SolverDispatcher.dispatch_calculation(self.current_form_key, payload)
        self.is_calculating = False

    # --- Exportaciones ---
    @rx.event
    def open_pdf_dialog(self):
        if self.current_form_key:
            self.pdf_filename = f"Informe_{self.current_form_key}.pdf"
        self.is_pdf_dialog_open = True

    @rx.event
    def export_pdf_to_server(self):
        self.is_pdf_dialog_open = False
        config_dict = FORM_REGISTRY.get(self.current_form_key, {})
        payload = ExportPayloadService.create_report_data(config_dict, self)
        return PDFExportProvider.save_pdf_to_server(payload, self.save_path, self.pdf_filename)

    @rx.event
    def open_excel_dialog(self):
        if self.current_form_key:
            self.excel_filename = f"Calculo_{self.current_form_key}.xlsx"
        self.is_excel_dialog_open = True

    @rx.event
    def export_excel_to_server(self):
        from structural_app.shared.infrastructure.excel_export import ExcelExportProvider
        self.is_excel_dialog_open = False
        config_dict = FORM_REGISTRY.get(self.current_form_key, {})
        payload = ExportPayloadService.create_report_data(config_dict, self)
        return ExcelExportProvider.save_excel_to_server(payload, self.save_path, self.excel_filename)

    # --- Navegación ---
    @rx.event
    async def navigate_to_form(self, key: str):
        self.results = SolverResponse(is_ok=True, checks=[], summary="Cargando...", plot_data=None)
        self.form_data = {}
        self.current_form_key = ""
        self.search_query = ""
        yield
        yield rx.redirect(f"/{key.replace('_', '-')}")

    @rx.event
    async def navigate_to_index(self):
        self.current_form_key = ""
        self.form_data = {}
        self.results = SolverResponse(is_ok=True, checks=[], summary="Esperando datos...", plot_data=None)
        self.last_calculation_hash = ""
        yield
        yield rx.redirect("/")

    # --- Búsqueda ---
    @rx.event
    def set_search_query(self, query: str): self.search_query = query
    @rx.event
    def clear_search(self): self.search_query = ""

    @rx.var
    def search_results(self) -> List[SearchResult]:
        if not self.search_query.strip(): return []
        q = self.search_query.lower()
        res = []
        for k, c in FORM_REGISTRY.items():
            if q in c.get("title", "").lower() or q in c.get("description", "").lower():
                res.append(SearchResult(title=c.get("title", ""), description=c.get("description", ""), form_key=k))
        return res

    # --- Gestión de Sesión (JSON) ---
    @rx.event
    def open_save_dialog(self):
        if self.current_form_key: self.save_filename = f"proyecto_{self.current_form_key}.json"
        self.is_save_dialog_open = True

    @rx.event
    def save_session(self):
        self.is_save_dialog_open = False
        payload_to_save = self.form_data.copy()
        payload_to_save["_form_key"] = self.current_form_key
        import datetime
        payload_to_save["_version_control"] = {
            "timestamp": datetime.datetime.now().isoformat(),
            "app_version": "1.1.0",
            "hash": self.last_calculation_hash,
            "user_tag": self.save_filename.replace(".json", "")
        }
        return SessionIO.save_to_server_disk(payload_to_save, self.save_path, self.save_filename)

    @rx.event
    async def load_session(self, files: list[rx.UploadFile]):
        if not files: return
        self.is_load_dialog_open = False
        yield
        file = files[0]
        upload_data = await file.read()
        content = upload_data.decode("utf-8")
        try:
            import json
            parsed_data = json.loads(content)
            origen = parsed_data.get("_form_key")
            if origen and origen != self.current_form_key:
                yield rx.toast.info(f"Detectado archivo de '{origen}'. Redirigiendo...")
                self.current_form_key = origen
                self.form_data = parsed_data
                yield rx.redirect(f"/{origen.replace('_', '-')}")
                yield BaseState.calculate()
                return
            self.form_data = parsed_data
            yield BaseState.calculate()
            yield rx.toast.success("Proyecto cargado con éxito")
        except Exception as e:
            yield rx.toast.error(f"Error al leer el archivo JSON: {str(e)}")

    # -----------------------------------------------------------------------
    # active_form_config — construye FormConfig inyectando has_tabs
    # -----------------------------------------------------------------------
    @rx.var
    def active_form_config(self) -> FormConfig:
        raw = FORM_REGISTRY.get(self.current_form_key, {})
        if not raw:
            return FormConfig()
        has_tabs = "tabs" in raw and len(raw["tabs"]) > 0
        return FormConfig(**raw, has_tabs=has_tabs)

    @rx.var
    def visualizer_title(self) -> str:
        features = self.active_form_config.features
        if features.get("viewer_3d", False): return "Modelo 3D Interactivo"
        if features.get("svg", False): return "Esquema de la Sección"
        return "Análisis Gráfico"

    @rx.var
    def show_visualizer(self) -> bool:
        features = self.active_form_config.features
        wants_visuals = features.get("viewer_3d", False) or features.get("svg", False)
        has_data = self.results is not None and self.results.plot_data is not None
        return wants_visuals and has_data and self.current_form_key != ""

    # --- Setters de Interfaz ---
    @rx.event
    def set_save_path(self, path: str): self.save_path = path
    @rx.event
    def set_save_filename(self, name: str): self.save_filename = name
    @rx.event
    def set_pdf_filename(self, name: str): self.pdf_filename = name
    @rx.event
    def set_excel_filename(self, name: str): self.excel_filename = name
    @rx.event
    def set_is_save_dialog_open(self, o: bool): self.is_save_dialog_open = o
    @rx.event
    def set_is_load_dialog_open(self, o: bool): self.is_load_dialog_open = o
    @rx.event
    def set_is_pdf_dialog_open(self, o: bool): self.is_pdf_dialog_open = o
    @rx.event
    def set_is_excel_dialog_open(self, o: bool): self.is_excel_dialog_open = o

    @rx.event
    async def clear_state_on_index(self):
        self.current_form_key = ""
        self.form_data = {}
        self.results = SolverResponse(is_ok=True, checks=[], summary="Esperando datos...", plot_data=None)
        self.last_calculation_hash = ""
        yield

    def reset_form(self): return rx.call_script("window.location.reload();")