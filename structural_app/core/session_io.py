import json
import os
import reflex as rx
from typing import Dict, Any

class SessionIO:
    """Motor de serialización para guardar y cargar estados de cálculo."""

    @staticmethod
    def save_to_server_disk(state_data: Dict[str, Any], directory: str, filename: str):
        """Escribe el JSON directamente en el disco duro del servidor."""
        try:
            # Aseguramos que el nombre acabe en .json
            if not filename.endswith(".json"):
                filename += ".json"
                
            # Unimos la ruta y el nombre del archivo
            full_path = os.path.join(directory, filename)
            
            # Escribimos físicamente el archivo en el disco
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=4, ensure_ascii=False)
                
            # Devolvemos un mensaje de éxito en verde
            return rx.toast.success(f"Guardado correctamente en: {full_path}")
            
        except Exception as e:
            # Si la ruta no existe o no hay permisos, avisamos al usuario
            return rx.toast.error(f"Error al guardar: {str(e)}")

    @staticmethod
    def parse_upload(content: str) -> Dict[str, Any]:
        """Convierte el archivo subido de vuelta a diccionario."""
        try:
            return json.loads(content)
        except Exception:
            return {}