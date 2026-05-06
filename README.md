# README - Structural Hub

## Descripcion General
Structural Hub es una aplicacion web interactiva desarrollada con el framework Reflex (Python). Esta diseñada para facilitar el calculo, la comprobacion y el diseño de elementos estructurales como muros de contencion, vigas y secciones de hormigon armado.

El sistema utiliza una arquitectura basada en un registro dinamico de formularios (JSON) y un despachador de calculos que conecta la interfaz de usuario con motores de calculo especializados.

## Estructura del Proyecto
El proyecto se organiza de la siguiente manera:

- structural_app/: Directorio principal de la aplicacion.
  - core/: Logica central (registro de formularios, gestion de sesiones, despacho de calculos).
  - forms/: Modulos de elementos estructurales especificos (ej. muro, cortante_circular).
  - pages/: Definiciones de las paginas y rutas de la aplicacion.
  - shared/: Componentes reutilizables, modelos de dominio y herramientas de exportacion (PDF/Excel).
  - tests/: Suite de pruebas unitarias y de integracion.

## Requisitos Previos
Para ejecutar este proyecto, es necesario tener instalado:
1. Python 3.8 o superior.
2. Un entorno virtual (recomendado).
3. Librerias de calculo estructural especificas (ej. fhecor_structuralcodes).

## Instalacion

1. Clonar el repositorio o descargar los archivos.
2. Crear un entorno virtual:
   python -m venv .venv
3. Activar el entorno virtual:
   - Windows: .venv\Scripts\activate
   - Linux/Mac: source .venv/bin/activate
4. Instalar las dependencias de Reflex y el proyecto:
   pip install reflex pydantic plotly pandas openpyxl weasyprint
5. Instalar los paquetes de calculo necesarios (reemplazar con el comando correspondiente si es un paquete privado):
   pip install -e .

## Ejecucion

Para poner en marcha la aplicacion, sigue estos pasos:

1. Inicializar el entorno de Reflex (solo si es la primera vez):
   reflex init

2. Iniciar la aplicacion en modo desarrollo:
   reflex run

3. Acceder a la interfaz:
   Una vez que el servidor este corriendo, abre un navegador y entra en:
   http://localhost:3000

## Como añadir un nuevo elemento estructural
El sistema es extensible sin modificar el nucleo:
1. Crear una subcarpeta en structural_app/forms/.
2. Incluir un archivo 'config.json' con la definicion de los campos de entrada y unidades.
3. Crear un archivo 'adapter.py' que implemente la funcion 'calculate_element' para procesar los datos.

## Ejecucion de Pruebas
Para verificar que los adaptadores de calculo y el sistema funcionan correctamente, ejecuta:
pytest structural_app/tests/

## Autores y Licencia
Desarrollado por FHECOR Ingenieros Consultores.
Uso interno y restringido segun los terminos de la empresa.