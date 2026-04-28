import os

# Archivo de salida
output_file = "structural_app.txt"
# Carpeta a explorar
carpeta_objetivo = "./structural_app"

def generar_arbol(ruta, prefijo=""):
    """Genera una representación visual de la estructura de carpetas."""
    arbol = ""
    archivos = sorted(os.listdir(ruta))
    for i, nombre in enumerate(archivos):
        if nombre == '__pycache__' or nombre.startswith('.'):
            continue
        
        ruta_completa = os.path.join(ruta, nombre)
        es_ultimo = (i == len(archivos) - 1)
        conector = "└── " if es_ultimo else "├── "
        
        arbol += f"{prefijo}{conector}{nombre}\n"
        
        if os.path.isdir(ruta_completa):
            nuevo_prefijo = prefijo + ("    " if es_ultimo else "│   ")
            arbol += generar_arbol(ruta_completa, nuevo_prefijo)
    return arbol

with open(output_file, 'w', encoding='utf-8') as outfile:
    # 1. Escribir el árbol de directorios al inicio
    outfile.write("# ESTRUCTURA DEL PROYECTO\n")
    outfile.write("```text\n")
    outfile.write(f"{carpeta_objetivo}/\n")
    outfile.write(generar_arbol(carpeta_objetivo))
    outfile.write("```\n\n")
    outfile.write(f"{'='*60}\n\n")

    # 2. Recorrer y empaquetar archivos
    for root, dirs, files in os.walk(carpeta_objetivo):
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
            
        for file in files:
            # Solo procesamos extensiones deseadas
            if file.endswith(('.py', '.json')):
                filepath = os.path.join(root, file)
                extension = "python" if file.endswith('.py') else "json"
                
                outfile.write(f"### Archivo: {filepath}\n")
                outfile.write(f"```{extension}\n")
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read())
                except Exception as e:
                    outfile.write(f"# Error leyendo archivo: {e}\n")
                
                outfile.write("\n```\n\n")

print(f"¡Listo! Estructura y código guardados en '{output_file}'.")