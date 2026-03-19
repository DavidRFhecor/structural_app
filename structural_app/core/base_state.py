import reflex as rx
from typing import Dict, Any, List, Optional
from pydantic import BaseModel # Usamos Pydantic para tipado fuerte
from structural_app.core.form_registry import FORM_REGISTRY
from structural_app.core.session_io import SessionIO

# 1. Definimos las estructuras de datos con Pydantic
# Esto permite que Reflex sepa exactamente qué hay dentro de cada lista
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
    fields: List[FormField] = [] # Tipado explícito para rx.foreach

class FormConfig(BaseModel):
    form_key: str = ""
    title: str = ""
    description: str = ""
    groups: List[FormGroup] = [] # Tipado explícito para rx.foreach
    tables: List[Dict[str, Any]] = []

# 2. El Estado Base de la aplicación
class BaseState(rx.State):
    current_form_key: str = ""
    is_calculating: bool = False
    last_error: str = ""

    # Variable para guardar lo que escribe el usuario
    search_query: str = ""

    @rx.var
    def active_form_config(self) -> FormConfig:
        """Retorna la configuración tipada. Clave para evitar errores de compilación."""
        raw_config = FORM_REGISTRY.get(self.current_form_key, {})
        # Convertimos el diccionario crudo a nuestro modelo Pydantic
        return FormConfig(**raw_config) if raw_config else FormConfig()

    @rx.event
    def set_value(self, field: str, value: str):
        """Convierte los strings de los inputs a float de forma segura."""
        try:
            # Si el input está vacío o es solo un signo menos, usamos 0.0
            if value.strip() in ["", "-"]:
                clean_value = 0.0
            else:
                clean_value = float(value)
            
            # Ahora setattr recibe un float real, no un string
            setattr(self, field, clean_value)
        except ValueError:
            # Si el usuario escribe algo no numérico, ignoramos el cambio
            pass
            
    @rx.var
    def search_results(self) -> List[SearchResult]:
        """Busca coincidencias en el registro de formularios en tiempo real."""
        if not self.search_query.strip():
            return []
            
        query = self.search_query.lower()
        results = []
        
        # Buscamos en todos los formularios registrados
        for key, config in FORM_REGISTRY.items():
            title = config.get("title", "").lower()
            desc = config.get("description", "").lower()
            
            # Si el texto coincide con el título o la descripción, lo añadimos
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
        """Limpia el buscador (útil al hacer clic en un resultado)."""
        self.search_query = ""

    def navigate_to_form(self, form_key: str):
        self.current_form_key = form_key
        return rx.redirect(f"/{form_key.replace('_', '-')}")

    def reset_form(self):
        self.last_error = ""
        return rx.window_reload()

    def save_session(self):
        data = {
            k: v for k, v in self.__dict__.items() 
            if not k.startswith("_") and isinstance(v, (float, int, str, list, dict))
        }
        return SessionIO.export_to_json(data, f"diseño_{self.current_form_key}.json")

    async def load_session(self, files: list[rx.UploadFile]):
        if not files: return
        data = await SessionIO.import_from_json(files[0])
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        yield rx.toast.info("Datos cargados correctamente")
    
    def set_search_query(self, query: str):
        self.search_query = query