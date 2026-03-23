import reflex as rx
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from structural_app.core.form_registry import FORM_REGISTRY
from structural_app.core.session_io import SessionIO

# ==========================================================
# 1. MODELOS DE DATOS (PYDANTIC)
# ==========================================================

class FormField(BaseModel):
    id: str = ""
    label: str = ""
    unit: str = ""
    default: Any = 0.0

class SearchResult(BaseModel):
    title: str = ""
    description: str = ""
    form_key: str = ""

class FormGroup(BaseModel):
    name: str = ""
    fields: List[FormField] = []

class FormConfig(BaseModel):
    form_key: str = ""
    title: str = ""
    description: str = ""
    groups: List[FormGroup] = []
    tables: List[Dict[str, Any]] = []

# ==========================================================
# 2. ESTADO BASE (BaseState)
# ==========================================================

class BaseState(rx.State):
    # --- Variables de Navegación y Control ---
    current_form_key: str = ""
    is_calculating: bool = False
    last_error: str = ""
    search_query: str = ""
    
    # --- Gestión de Archivos ---
    save_filename: str = "proyecto_calculo.json"
    save_path: str = "./"
    is_save_dialog_open: bool = False
    is_load_dialog_open: bool = False

    # --- SETTERS BÁSICOS ---

    @rx.event
    def set_search_query(self, query: str):
        self.search_query = query

    @rx.event
    def set_save_path(self, path: str):
        self.save_path = path

    @rx.event
    def set_save_filename(self, name: str):
        self.save_filename = name

    @rx.event
    def set_is_save_dialog_open(self, is_open: bool):
        self.is_save_dialog_open = is_open

    @rx.event
    def set_is_load_dialog_open(self, is_open: bool):
        self.is_load_dialog_open = is_open

    # --- SMART SETTER (EL ARREGLO CRÍTICO) ---
    @rx.event
    def set_value(self, field: str, value: str):
        """
        Setter Universal corregido según la sugerencia de Reflex.
        """
        try:
            # 1. Limpieza y conversión
            val_strip = value.strip()
            if val_strip in ["", "-", "."]:
                clean_value = 0.0
            else:
                clean_value = float(value.replace(",", "."))
            
            # 2. ¿La variable está en el estado actual?
            if hasattr(self, field):
                setattr(self, field, clean_value)
                return

            # 3. ¿La variable está en alguna de las hijas (substates)?
            # Quitamos el '_' según nos indica el error
            for substate in self.substates.values():
                if hasattr(substate, field):
                    setattr(substate, field, clean_value)
                    return

            # 4. Si no se encuentra, avisamos por consola
            print(f"Aviso: No se encontró '{field}' en {self.__class__.__name__} ni en sus hijos.")

        except (ValueError, TypeError):
            pass

    # --- GESTIÓN DE SESIÓN (GUARDAR/CARGAR) ---

    @rx.event
    def open_save_dialog(self):
        """Prepara el nombre del archivo según el formulario activo."""
        if self.current_form_key:
            self.save_filename = f"proyecto_{self.current_form_key}.json"
        self.is_save_dialog_open = True

    @rx.event
    def save_session(self):
        """Recopila datos del formulario actual y genera la descarga."""
        self.is_save_dialog_open = False 
        raw_config = FORM_REGISTRY.get(self.current_form_key, {})
        data = {}
        
        # Extraemos datos de los grupos de campos
        for group in raw_config.get("groups", []):
            for field in group.get("fields", []):
                field_id = field.get("id")
                if field_id and hasattr(self, field_id):
                    data[field_id] = getattr(self, field_id)
                    
        # Extraemos datos de las tablas
        for table in raw_config.get("tables", []):
            table_id = table.get("id")
            if table_id and hasattr(self, table_id):
                data[table_id] = getattr(self, table_id)
                
        clean_name = self.save_filename.replace(".json", "")
        # Llama a tu utilidad de descarga
        return SessionIO.download_state(data, clean_name)

    @rx.event
    async def load_session(self, files: list[rx.UploadFile]):
        """Carga un archivo JSON y actualiza las variables del estado."""
        if not files: 
            return
            
        try:
            file_content = await files[0].read()
            data = SessionIO.parse_upload(file_content.decode('utf-8'))
            
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            
            self.is_load_dialog_open = False 
            yield rx.toast.success("¡Proyecto cargado con éxito!")
        except Exception as e:
            yield rx.toast.error(f"Error al cargar el archivo: {str(e)}")

    # --- LÓGICA DE FORMULARIOS ---

    @rx.var
    def active_form_config(self) -> FormConfig:
        """Retorna la configuración del formulario actual tipada con Pydantic."""
        raw_config = FORM_REGISTRY.get(self.current_form_key, {})
        return FormConfig(**raw_config) if raw_config else FormConfig()

    @rx.var
    def search_results(self) -> List[SearchResult]:
        """Busca formularios en el registro global."""
        if not self.search_query.strip():
            return []
            
        query = self.search_query.lower()
        results = []
        
        for key, config in FORM_REGISTRY.items():
            title = config.get("title", "").lower()
            desc = config.get("description", "").lower()
            
            if query in title or query in desc:
                results.append(
                    SearchResult(
                        title=config.get("title", ""),
                        description=config.get("description", ""),
                        form_key=key
                    )
                )
        return results

    def clear_search(self):
        self.search_query = ""

    def navigate_to_form(self, form_key: str):
        self.current_form_key = form_key
        self.clear_search()
        return rx.redirect(f"/{form_key.replace('_', '-')}")

    def reset_form(self):
        """Recarga la página para limpiar todos los inputs."""
        return rx.call_script("window.location.reload();")