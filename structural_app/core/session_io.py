import json
import reflex as rx
from typing import Dict, Any

class SessionIO:
    """Motor de serialización para guardar y cargar estados de cálculo."""

    @staticmethod
    def download_state(state_data: Dict[str, Any], filename: str):
        """Genera el archivo para el navegador."""
        # Limpiamos datos que no son serializables (como funciones o objetos complejos)
        serializable_data = {
            k: v for k, v in state_data.items() 
            if isinstance(v, (str, int, float, bool, list, dict))
        }
        
        return rx.download(
            data=json.dumps(serializable_data, indent=4),
            filename=f"{filename}.json"
        )

    @staticmethod
    def parse_upload(content: str) -> Dict[str, Any]:
        """Convierte el archivo subido de vuelta a diccionario."""
        try:
            return json.loads(content)
        except Exception:
            return {}