import reflex as rx
from structural_app.core.form_registry import FormRegistry
from structural_app.core.logger_config import init_logger
from structural_app.pages.index import index
from structural_app.shared.components.generic_page import generic_form_page
from structural_app.core.base_state import BaseState

def create_full_app():
    init_logger()
    app = rx.App(
        stylesheets=[
            "https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&display=swap",
            "styles.css",  # Quita la barra inicial si "/" falla en Windows
        ],
        style={
            "font_family": "Lato",
            "color": "rgb(0, 50, 100)", # Azul corporativo FHECOR [cite: 6]
        }
    )

    app.add_page(
        index, 
        route="/", 
        title="Structural Hub", 
        on_load=BaseState.clear_state_on_index 
    )
    # Usamos la clave del registro (normalmente el nombre de la carpeta del formulario)
    # para evitar fallos cuando algún `config.json` no incluya `form_key`.
    for key, form in FormRegistry.items():
        app.add_page(
            generic_form_page, 
            route=f"/{key.replace('_', '-')}", 
            title=f"{form.get('title', key)} | FHECOR",
            on_load=BaseState.set_current_form(key) 
        )
    return app

app = create_full_app()