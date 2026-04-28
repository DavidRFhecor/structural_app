from typing import Dict, Any

class ExportPayloadService:
    """Prepara los datos del State para los motores de impresión (PDF/Excel)."""

    @staticmethod
    def create_report_data(config: Dict[str, Any], state: Any) -> Dict[str, Any]:
        """Extrae la información relevante para el informe final."""
        return {
            "project_info": {
                "title": config.get("title"),
                "category": config.get("category"),
                "date": "2026-03-17", # Fecha actual
            },
            "inputs": [
                {
                    "group": group["name"],
                    "fields": [
                        {
                            "label": f["label"],
                            "value": state.form_data.get(f["id"], 0.0),
                            "unit": f.get("unit", "")
                        } for f in group["fields"]
                    ]
                } for group in config.get("groups", [])
            ],
            "results": {
                "is_ok": state.results.is_ok,
                "summary": state.results.summary,
                "checks": [
                    {
                        "desc": c.description,
                        "val": f"{c.value} {c.unit}",
                        "lim": f"{c.limit} {c.unit}",
                        "ratio": f"{c.ratio:.2f}",
                        "status": "CUMPLE" if c.status else "NO CUMPLE"
                    } for c in state.results.checks
                ]
            }
        }