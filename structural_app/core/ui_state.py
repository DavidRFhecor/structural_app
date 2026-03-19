import reflex as rx
from typing import List
from .form_registry import FORM_REGISTRY

class UIState(rx.State):
    """Estado global para la navegación y preferencias de interfaz."""
    
    search_query: str = ""
    is_sidebar_open: bool = True
    dark_mode: bool = False
    
    @rx.var
    def filtered_forms(self) -> List[dict]:
        """Filtra las calculadoras disponibles según el buscador del index."""
        if not self.search_query:
            return list(FORM_REGISTRY.values())
        
        return [
            config for config in FORM_REGISTRY.values()
            if self.search_query.lower() in config["title"].lower() 
            or self.search_query.lower() in config.get("category", "").lower()
        ]

    def toggle_sidebar(self):
        self.is_sidebar_open = not self.is_sidebar_open

    def set_search(self, query: str):
        self.search_query = query