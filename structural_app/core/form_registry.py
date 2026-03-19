import os
import json
from typing import Dict, Any

def discover_forms() -> Dict[str, Any]:
    """Escanea y registra formularios dinámicamente."""
    registry = {}
    base_dir = os.path.join("structural_app", "forms")
    
    if not os.path.exists(base_dir):
        return registry

    for folder in os.listdir(base_dir):
        # Ignorar plantillas y archivos privados
        if folder.startswith(("_", ".")):
            continue
            
        config_path = os.path.join(base_dir, folder, "config.json")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                registry[folder] = config
    return registry

FORM_REGISTRY = discover_forms()
FormRegistry = FORM_REGISTRY