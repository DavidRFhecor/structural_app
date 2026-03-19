import json
import os
from typing import Dict, Any, Optional

class ConfigLoader:
    """Servicio para cargar y validar los JSON de cada formulario."""

    @staticmethod
    def load(form_folder: str) -> Optional[Dict[str, Any]]:
        config_path = os.path.join("structural_app", "forms", form_folder, "config.json")
        
        if not os.path.exists(config_path):
            return None
            
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                
            # Validación de campos mínimos obligatorios del contrato
            required_keys = ["form_key", "title", "groups", "template_type"]
            if not all(key in config for key in required_keys):
                print(f"Configuración incompleta en: {form_folder}")
                return None
                
            return config
        except Exception as e:
            print(f"Error crítico leyendo config.json en {form_folder}: {e}")
            return None