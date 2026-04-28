import os
import json

def scaffold_form(key_name: str, title: str):
    base_path = f"structural_app/forms/{key_name}"
    os.makedirs(base_path, exist_ok=True)
    
    # 1. Crea el __init__.py vacío
    open(f"{base_path}/__init__.py", "a").close()
    
    # 2. Crea un config.json base
    config = {
        "form_key": key_name,
        "title": title,
        "template_type": "single_check_form",
        "groups": [{"name": "Datos Base", "fields": [{"id": "param1", "label": "Parámetro 1", "unit": "m", "default": 1.0}]}],
        "features": {"svg": False, "viewer_3d": False}
    }
    with open(f"{base_path}/config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
        
    # 3. Crea el adapter.py base
    adapter_code = """from structural_app.shared.domain.result_models import SolverResponse, CheckResult

def calculate_element(param1=1.0, **kwargs):
    # Escribe tu lógica aquí
    resultado = param1 * 2
    
    return SolverResponse(
        is_ok=True,
        summary="Cálculo exitoso.",
        checks=[CheckResult(description="Comprobación 1", status=True, value=resultado, limit=10.0)]
    )
"""
    with open(f"{base_path}/adapter.py", "w", encoding="utf-8") as f:
        f.write(adapter_code)
        
    print(f"Módulo '{title}' ({key_name}) creado con éxito en {base_path}!")

# Uso: python crear_modulo.py zapata_aislada "Zapata Aislada"
if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3:
        scaffold_form(sys.argv[1], sys.argv[2])
    else:
        print("Uso: python crear_modulo.py <nombre_carpeta> <Titulo>")