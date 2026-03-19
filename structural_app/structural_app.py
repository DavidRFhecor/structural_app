import reflex as rx
import importlib
import sys
import types

# =========================================================================
# 🛠️ PUENTES DE COMPATIBILIDAD (Ejecutar antes de cargar la App)
# =========================================================================

import structuralcodes
from structuralcodes import sections
import structuralcodes.geometry

# 1. Parche para Geometría (LineGeometry desaparecida)
if not hasattr(structuralcodes.geometry, 'LineGeometry'):
    structuralcodes.geometry.LineGeometry = structuralcodes.geometry.Geometry

# 2. Puente para structuralcodes.core.section -> structuralcodes.sections
# Esto soluciona el error "No module named 'structuralcodes.core.section'"
core_mod = types.ModuleType("structuralcodes.core")
sys.modules["structuralcodes.core"] = core_mod

section_mod = types.ModuleType("structuralcodes.core.section")
sys.modules["structuralcodes.core.section"] = section_mod

# Mapeamos la clase que busca FHECOR (Section) a la nueva (GenericSection)
section_mod.Section = sections.GenericSection
core_mod.section = section_mod

print("✅ Puentes de compatibilidad activados: LineGeometry y Core.Section.")

# =========================================================================
# 🚀 IMPORTACIONES DE LA APP
# =========================================================================

from structural_app.core.form_registry import FormRegistry
from structural_app.core.config_loader import ConfigLoader
from structural_app.core.logger_config import init_logger
from structural_app.pages.index import index

def create_full_app():
    # Inicialización de servicios core
    init_logger()
    
    # Podrías descomentar esto si quieres cargar configuraciones de JSON/YAML
    # ConfigLoader.load_all_forms()

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

    # 1. Registrar el Dashboard Principal (Página de inicio)
    app.add_page(index, route="/", title="Structural Hub | Home")

    # 2. Registro dinámico de formularios (Módulos de cálculo)
    for form in FormRegistry.values():
        key = form["form_key"]
        try:
            # Construimos la ruta del módulo dinámicamente
            module_path = f"structural_app.forms.{key}.page"
            module = importlib.import_module(module_path)
            
            # Buscamos la función de la página (ej: beam_double_t_page)
            page_component = getattr(module, f"{key}_page")
            
            # Normalizamos la ruta (ej: beam_double_t -> /beam-double-t)
            route = f"/{key.replace('_', '-')}"
            
            app.add_page(
                page_component, 
                route=route, 
                title=f"{form['title']} | FHECOR"
            )
            print(f"✔️ Formulario registrado: {key} en {route}")
            
        except Exception as e:
            print(f"❌ Error registrando el formulario {key}: {e}")

    return app

# Instancia global de la aplicación
app = create_full_app()