import importlib
import os
import inspect
import math
from typing import Dict, Any, List
from structural_app.shared.domain.result_models import SolverResponse, CheckResult
from structural_app.core.form_registry import FORM_REGISTRY

class SolverDispatcher:
    @staticmethod
    def dispatch_calculation(form_key: str, payload: Dict[str, Any]) -> SolverResponse:
        config = FORM_REGISTRY.get(form_key, {})
        norm_v = config.get("norm_version", "ec2_2004")
        
        # 1. Intentar usar Adaptador (Solo si existe físicamente)
        adapter_path = os.path.join("structural_app", "forms", form_key, "adapter.py")
        if os.path.exists(adapter_path):
            try:
                module_path = f"structural_app.forms.{form_key}.adapter"
                adapter = importlib.import_module(module_path)
                
                if hasattr(adapter, "calculate_element"):
                    return adapter.calculate_element(payload)
            except Exception as e:
                print(f"Aviso: Adaptador falló ({e}). Usando modo automático...")

        # 2. Motor Automático Universal (Cero código en el formulario)
        return SolverDispatcher.execute_auto_logic(config, norm_v, payload)

    @staticmethod
    def execute_auto_logic(config: Dict[str, Any], norm_v: str, payload: Dict[str, Any]) -> SolverResponse:
        try:
            logic_cfg = config.get("logic", {})
            func_name = logic_cfg.get("function")
            
            if not func_name:
                return SolverResponse(is_ok=False, summary="Error: No hay 'logic.function' en el JSON.", checks=[])

            norm_lib = importlib.import_module(f"fhecor_structuralcodes.checks_{norm_v}")
            func = getattr(norm_lib, func_name)

            # --- VALORES POR DEFECTO INTELIGENTES ---
            asl_val = payload.get("asl", payload.get("as_principal", 0.0))
            
            defaults = {
                "asw": 0.0, "s": 100.0, "ned": 0.0, 
                "theta": 45.0, "sismic_comb": False,
                "asl": asl_val
            }

            # Cálculo de Ac (Área de concreto) dinámico
            if "Ac" not in payload:
                if "bw" in payload and "h" in payload:
                    defaults["Ac"] = payload["bw"] * payload["h"]
                elif "bw" in payload:
                    # Sección circular (bw es diámetro)
                    defaults["Ac"] = math.pi * (payload["bw"] / 2)**2

            if "z" not in payload and "d" in payload:
                defaults["z"] = 0.9 * payload["d"]

            full_data = {**defaults, **payload}

            # Filtrado: solo enviamos lo que la función de FHECOR pide
            sig = inspect.signature(func)
            clean_payload = {k: v for k, v in full_data.items() if k in sig.parameters}
            
            results_dict, _ = func(**clean_payload)
            
            # --- GENERACIÓN DE RESULTADOS ---
            checks = []
            for out in logic_cfg.get("outputs", []):
                raw_val = results_dict.get(out["key"], 0.0)
                final_val = raw_val * out.get("factor", 1.0)
                
                # Obtener la clave de comparación del JSON ("compare_against")
                compare_key = out.get("compare_against")
                
                # Rescatar ese valor de los inputs del usuario
                limit_val = full_data.get(compare_key, 0.0) if compare_key else 0.0
                
                # Calcular el estado real: Resistencia >= Solicitación
                # Cambiado para asegurar que el estado global sea coherente con los checks individuales
                status_val = final_val >= limit_val if compare_key else True
                
                checks.append(CheckResult(
                    description=out["label"],
                    status=status_val,
                    value=round(final_val, 3),
                    limit=round(limit_val, 3),
                    unit=out["unit"]
                ))
            
            # El estado global is_ok es True solo si TODOS los checks individuales cumplen
            return SolverResponse(
                is_ok=all(c.status for c in checks), 
                summary="Cálculo automático completado.", 
                checks=checks
            )
             
        except Exception as e:
            return SolverResponse(is_ok=False, summary=f"Error en motor automático: {str(e)}", checks=[])