import reflex as rx
from ....core.base_state import BaseState
from ....shared.components.data_table import custom_data_table

class ComplexState(BaseState):
    # Datos de la tabla inicializados como lista de diccionarios (estándar Reflex)
    datos_tabla: list[dict] = [{"ID": "Fase 1", "Magnitud": 100.0}]

    def update_table(self, pos, val):
        """Actualiza la celda editada en la tabla."""
        col, row = pos
        col_name = self.active_form_config["tables"][0]["columns"][col]["title"]
        self.datos_tabla[row][col_name] = val

    async def calculate(self):
        # Aquí el DTO recogería tanto campos simples como self.datos_tabla
        pass