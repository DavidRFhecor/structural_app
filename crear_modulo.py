import os
import json
import argparse

def crear_estructura_modulo(nombre_modulo, con_adaptador=False):
    # 1. Definir rutas basándose en la estructura del proyecto [cite: 1, 107]
    base_path = os.path.join("structural_app", "forms", nombre_modulo)
    
    if os.path.exists(base_path):
        print(f"Error: El módulo '{nombre_modulo}' ya existe.")
        return

    os.makedirs(base_path, exist_ok=True)

    # 2. Crear config.json (Esqueleto para UI y Lógica Automática) [cite: 138, 139]
    config_data = {
        "form_key": nombre_modulo,
        "title": nombre_modulo.replace("_", " ").title(),
        "description": f"Módulo para el cálculo de {nombre_modulo.replace('_', ' ')}.",
        "norm_version": "ec2_2004",
        "logic": {
            "function": "nombre_de_la_funcion_en_fhecor",
            "outputs": [
                {
                    "key": "resultado_clave",
                    "label": "Resultado Principal",
                    "unit": "kN",
                    "factor": 1.0,
                    "compare_against": "solicitacion_id"
                }
            ]
        },
        "groups": [
            {
                "name": "Datos de Entrada",
                "fields": [
                    { "id": "bw", "label": "Ancho (b)", "unit": "mm", "default": 300.0 },
                    { "id": "solicitacion_id", "label": "Carga", "unit": "kN", "default": 100.0 }
                ]
            }
        ],
        "features": { "svg": False, "viewer_3d": False, "sketch": True }
    }

    with open(os.path.join(base_path, "config.json"), "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4, ensure_ascii=False)

    # 3. Crear __init__.py [cite: 1]
    with open(os.path.join(base_path, "__init__.py"), "w") as f:
        f.write("")

    # 4. Crear adapter.py (Opcional, para lógica personalizada) [cite: 115, 116]
    if con_adaptador:
        adapter_content = f"""from pydantic import BaseModel, Field
from structural_app.shared.domain.result_models import SolverResponse, CheckResult

class InputModel(BaseModel):
    bw: float = Field(gt=0)
    solicitacion_id: float

def calculate_element(payload: dict) -> SolverResponse:
    # El SolverDispatcher limpia los metadatos antes de llamar al adaptador [cite: 132]
    payload.pop("_features", None)
    
    try:
        inputs = InputModel(**payload)
        # Aquí iría la lógica de llamada a fhecor_structuralcodes [cite: 133, 134]
        
        checks = [
            CheckResult(
                description="Comprobación ejemplo",
                status=True,
                value=inputs.bw,
                limit=500.0,
                unit="mm"
            )
        ]
        return SolverResponse(is_ok=True, summary="Cálculo realizado", checks=checks)
    except Exception as e:
        return SolverResponse(is_ok=False, summary=f"Error: {{str(e)}}", checks=[])
"""
        with open(os.path.join(base_path, "adapter.py"), "w", encoding="utf-8") as f:
            f.write(adapter_content)

    print(f"Módulo '{nombre_modulo}' creado con éxito en {base_path}")
    print(f"Recuerda que el sistema lo registrará automáticamente al reiniciar la app[cite: 106, 107].")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generador de módulos para Structural Hub")
    parser.add_argument("nombre", help="Nombre del módulo (ej: zapata_aislada)")
    parser.add_argument("--adapter", action="store_true", help="Crear archivo adapter.py")
    
    args = parser.parse_args()
    crear_estructura_modulo(args.nombre, args.adapter)