import json
import os
import reflex as rx
from typing import Dict, Any

class SessionIO:
    """Motor de persistencia para guardar y cargar estados en el disco del servidor."""

    @staticmethod
    def resolve_path(directory: str) -> str:
        """Convierte atajos como 'descargas' en rutas absolutas del sistema."""
        dir_limpio = directory.strip() if directory else ""
        
        # Detecta si el usuario quiere la carpeta de Descargas del sistema
        if dir_limpio.lower() in ["descargas", "downloads"]:
            return os.path.join(os.path.expanduser('~'), 'Downloads')
            
        return dir_limpio if dir_limpio != "" else "./"

    @staticmethod
    def save_to_server_disk(state_data: Dict[str, Any], directory: str, filename: str):
        """Escribe el JSON directamente en el disco duro."""
        try:
            if not filename.endswith(".json"):
                filename += ".json"

            # Usamos el resolvedor para la ruta
            directory = SessionIO.resolve_path(directory)
            os.makedirs(directory, exist_ok=True)
            
            full_path = os.path.join(directory, filename)
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=4, ensure_ascii=False)
                
            return rx.toast.success(f"Sesión guardada en: {full_path}")
        except Exception as e:
            return rx.toast.error(f"Error al guardar sesión: {str(e)}")
            
    @staticmethod
    def list_versions(directory: str, form_key: str) -> list:
        """Busca archivos JSON que coincidan con el formulario actual."""
        path = SessionIO.resolve_path(directory)
        if not os.path.exists(path): return []
        
        files = [f for f in os.listdir(path) if f.endswith(".json") and form_key in f]
        return sorted(files, reverse=True) # Las más recientes primero