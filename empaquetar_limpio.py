import os

# Archivo de salida
output_file = "structural_app.txt"

# SOLO vamos a leer la carpeta interna donde está tu código real
# Ignoramos la raíz donde están los entornos virtuales (.venv, .web, etc)
carpeta_objetivo = "./structural_app"

with open(output_file, 'w', encoding='utf-8') as outfile:
    for root, dirs, files in os.walk(carpeta_objetivo):
        
        # Ignoramos la caché de Python si nos la cruzamos
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
            
        for file in files:
            # Solo queremos Python y JSON
            if file.endswith('.py') or file.endswith('.json'):
                filepath = os.path.join(root, file)
                
                outfile.write(f"\n\n{'='*60}\n")
                outfile.write(f"📁 ARCHIVO: {filepath}\n")
                outfile.write(f"{'='*60}\n\n")
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read())
                except Exception as e:
                    outfile.write(f"# Error leyendo archivo: {e}\n")

print(f"¡Listo! Revisa '{output_file}'. Debería pesar poquísimo.")