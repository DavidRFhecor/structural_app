import reflex as rx
import importlib
from structural_app.core.form_registry import FormRegistry
from structural_app.core.config_loader import ConfigLoader
from structural_app.core.logger_config import init_logger
from structural_app.pages.index import index

def create_full_app():
    # Inicialización de servicios core
    init_logger()
    #ConfigLoader.load_all_forms()

    app = rx.App(
        style={
            "font_family": "Inter",
            "background_color": "#f9fafb"
        },
        theme=rx.theme(
            appearance="light",
            has_background=True,
            accent_color="blue",
        )
    )

    # 1. Registrar el Dashboard Principal
    app.add_page(index, route="/", title="Structural Hub | Home")

# 2. Registro dinámico de formularios
    for form in FormRegistry.values():  # <--- Añadidos los :
        key = form["form_key"]          # <--- Todo este bloque movido a la derecha
        try:
            module_path = f"structural_app.forms.{key}.page"
            module = importlib.import_module(module_path)
            page_component = getattr(module, f"{key}_page")
            route = f"/{key.replace('_', '-')}"
            
            app.add_page(
                page_component, 
                route=route, 
                title=f"{form['title']} | FHECOR"
            )
        except Exception as e:
            print(f"Error registrando el formulario {key}: {e}")

    return app

app = create_full_app()