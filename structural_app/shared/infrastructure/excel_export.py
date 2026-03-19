import reflex as rx
import pandas as pd
import io

class ExcelExportProvider:
    """Generador de archivos Excel basados en el estado del cálculo."""

    @staticmethod
    def generate_excel_report(payload: dict):
        """
        Convierte el payload de resultados en un archivo .xlsx descargable.
        """
        # Creamos un buffer en memoria
        output = io.BytesIO()
        
        # Estructuramos los datos para pandas
        df_inputs = pd.DataFrame([
            {"Parámetro": f["label"], "Valor": f["value"], "Unidad": f["unit"]}
            for group in payload["inputs"] for f in group["fields"]
        ])
        
        df_checks = pd.DataFrame(payload["results"]["checks"])

        # Escribimos con varias pestañas
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_inputs.to_excel(writer, sheet_name='Entradas', index=False)
            df_checks.to_excel(writer, sheet_name='Resultados', index=False)
            
        return rx.download(
            data=output.getvalue(),
            filename=f"Calculo_{payload['project_info']['title']}.xlsx",
        )