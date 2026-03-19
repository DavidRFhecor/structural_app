import os
import shutil

def create_form(name, type="element_design_form"):
    """
    Copia el template y reemplaza los placeholders.
    Uso: python scaffold.py mi_zapata element_design_form
    """
    src = f"structural_app/forms/_templates/{type}"
    dst = f"structural_app/forms/{name}"
    
    shutil.copytree(src, dst)
    
    # Renombrado de archivos .template
    for f in os.listdir(dst):
        if "template" in f:
            new_f = f.replace("_template", "").replace(".template", "")
            os.rename(os.path.join(dst, f), os.path.join(dst, new_f))
    
    print(f"🏗️ Estructura para '{name}' lista. ¡A calcular!")
