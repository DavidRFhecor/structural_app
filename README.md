## Hub de Cálculo Estructural - FHECOR

Aplicación web profesional para el diseño y comprobación normativa de elementos estructurales, basada en **Reflex** y el motor matemático **fhecor_structuralcodes**.

##  Arquitectura
- **Core**: Gestión de estados, sesiones y despacho de cálculos.
- **Forms**: Módulos independientes por tipo de elemento (Muro, Viga, etc.).
- **Shared**: Componentes UI 40/60, visor 3D y utilidades SVG.

##  Instalación
1. Clonar el repositorio.
2. Instalar dependencias: `pip install -r requirements.txt`.
3. Configurar el archivo `.env` con las credenciales de GitHub.
4. Ejecutar: `reflex run`.

##  Testing
Para ejecutar las pruebas de validación normativa:
```bash
pytest tests/

## Requisitos de Librerías (`pyproject.toml`)
Definimos las dependencias necesarias para soportar 3D, exportación y validación.

**Archivo:** `pyproject.toml`

```toml
[tool.poetry.dependencies]
python = "^3.11"
reflex = ">=0.4.0"
pydantic = "^2.0"
pandas = "^2.0"
xlsxwriter = "^3.0"
numpy = "^1.24"
# Motor externo de ingeniería
fhecor_structuralcodes = { git = "https://github.com/MestreCarlos/fhecor_structuralcodes.git" }