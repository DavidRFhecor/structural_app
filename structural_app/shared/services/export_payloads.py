import datetime
from typing import Dict, Any, List


class ExportPayloadService:
    """Prepara los datos del State para los motores de impresión (PDF/Excel)."""

    @staticmethod
    def _extract_groups(config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recorre tanto formularios con tabs como sin tabs y devuelve todos los grupos."""
        groups = []

        # Formularios con pestañas
        for tab in config.get("tabs", []):
            tab_label = tab.get("label", "")
            for group in tab.get("groups", []):
                if group.get("type") == "data_table":
                    continue  # las tablas se tratan aparte
                if group.get("fields"):
                    groups.append({
                        "tab": tab_label,
                        "group": group.get("name", group.get("id", "")),
                        "fields": group["fields"],
                    })

        # Formularios sin pestañas (legacy)
        if not groups:
            for group in config.get("groups", []):
                if group.get("type") == "data_table":
                    continue
                if group.get("fields"):
                    groups.append({
                        "tab": "",
                        "group": group.get("name", group.get("id", "")),
                        "fields": group["fields"],
                    })

        return groups

    @staticmethod
    def create_report_data(config: Dict[str, Any], state: Any) -> Dict[str, Any]:
        """Extrae la información relevante para el informe final."""
        groups = ExportPayloadService._extract_groups(config)

        inputs = []
        for g in groups:
            fields = []
            for f in g["fields"]:
                field_id   = f.get("id") or f.get("name")
                field_type = f.get("type", "number")

                # Ignorar campos no editables
                if field_type in ("derived", "calculation_trigger", "info_label"):
                    continue

                raw_value = state.form_data.get(field_id, f.get("default", ""))
                fields.append({
                    "label": f.get("label", field_id),
                    "value": raw_value,
                    "unit":  f.get("unit", ""),
                })

            if fields:
                inputs.append({
                    "tab":    g["tab"],
                    "group":  g["group"],
                    "fields": fields,
                })

        return {
            "project_info": {
                "title":    config.get("title", "Informe"),
                "category": config.get("category", ""),
                "date":     datetime.date.today().strftime("%d/%m/%Y"),
            },
            "inputs": inputs,
            "results": {
                "is_ok":   state.results.is_ok,
                "summary": state.results.summary,
                "checks": [
                    {
                        "desc":   c.description,
                        "val":    f"{c.value} {c.unit}",
                        "lim":    f"{c.limit} {c.unit}",
                        "ratio":  c.ratio,
                        "status": "CUMPLE" if c.status else "NO CUMPLE",
                    }
                    for c in state.results.checks
                ],
                "intermediate_tables": [
                    {
                        "title":   t.title,
                        "note":    t.note,
                        "columns": [col.dict() for col in t.columns],
                        "rows":    t.rows,
                    }
                    for t in (state.results.intermediate_tables or [])
                ],
            },
        }