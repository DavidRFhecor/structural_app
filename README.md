# Structural App

Aplicación web de cálculo estructural desarrollada con [**Reflex**](https://reflex.dev/) (Python full-stack). Permite a ingenieros introducir datos en formularios configurables, ejecutar verificaciones normativas automáticas y exportar los resultados en PDF o Excel.

\---

## Tabla de contenidos

1. [Descripción general](#descripción-general)
2. [Arquitectura del proyecto](#arquitectura-del-proyecto)
3. [Tecnologías utilizadas](#tecnologías-utilizadas)
4. [Instalación y puesta en marcha](#instalación-y-puesta-en-marcha)
5. [Cómo añadir un nuevo formulario](#cómo-añadir-un-nuevo-formulario)
6. [Módulos principales](#módulos-principales)
7. [Exportación de resultados](#exportación-de-resultados)
8. [Gestión de sesión](#gestión-de-sesión)
9. [Tests](#tests)
10. [Convenciones y estilo de código](#convenciones-y-estilo-de-código)

\---

## Descripción general

Structural App es un hub de herramientas de cálculo estructural orientado a la normativa europea (Eurocódigos). Cada herramienta de cálculo —llamada **formulario**— se define mediante un archivo `config.json` y, opcionalmente, un `adapter.py` con lógica de cálculo personalizada. Si no existe adaptador, el motor universal del `SolverDispatcher` ejecuta las verificaciones de forma automática a partir de la configuración JSON.

La interfaz presenta una página de inicio con buscador de formularios y, para cada formulario, una página de cálculo con:

* Entrada de datos organizada en pestañas y grupos.
* Botón de **Calcular** que lanza las verificaciones normativas.
* Panel de resultados con comprobaciones (CUMPLE / NO CUMPLE) y gráficas interactivas.
* Exportación a PDF e Excel.
* Guardado y carga de sesiones en JSON.

\---

## Arquitectura del proyecto

```
structural\_app/
├── structural\_app.py          # Punto de entrada: crea la app Reflex y registra rutas
├── core/
│   ├── base\_state.py          # Estado global (rx.State): datos, cálculo, navegación, exportación
│   ├── form\_registry.py       # Descubrimiento automático de formularios (config.json)
│   ├── logger\_config.py       # Configuración del logger de la aplicación
│   ├── session\_io.py          # Persistencia de sesiones en disco (JSON)
│   └── solver\_dispatcher.py   # Enrutador de cálculo: adaptador custom o motor universal
├── forms/
│   └── <nombre\_formulario>/
│       ├── config.json        # Definición completa del formulario (campos, tabs, lógica)
│       └── adapter.py         # (Opcional) Lógica de cálculo específica
├── pages/
│   └── index.py               # Página de inicio con buscador
├── shared/
│   ├── components/            # Componentes Reflex reutilizables (layout, tablas, gráficas…)
│   ├── domain/
│   │   ├── constants.py       # Constantes globales (colores, etc.)
│   │   ├── material\_library.py# Biblioteca de materiales estructurales
│   │   └── result\_models.py   # Modelos Pydantic: SolverResponse, CheckResult
│   ├── infrastructure/
│   │   ├── excel\_export.py    # Generación de informes Excel
│   │   └── pdf\_export.py      # Generación de informes PDF (FPDF2)
│   └── services/
│       ├── export\_payloads.py # Prepara el payload para los exportadores
│       ├── hash\_service.py    # Hash SHA-256 de inputs para evitar cálculos redundantes
│       └── plot\_engine.py     # Motor de visualización Plotly con estilos corporativos
└── tests/
    ├── forms/                 # Tests por formulario (adapter, DTO, state)
    └── shared/                # Tests de servicios compartidos
```

\---

## Tecnologías utilizadas

|Tecnología|Uso|
|-|-|
|[Reflex](https://reflex.dev/)|Framework web Python full-stack (frontend + backend)|
|[Pydantic](https://docs.pydantic.dev/)|Modelos de datos y validación|
|[Plotly](https://plotly.com/python/)|Gráficas interactivas de resultados|
|[FPDF2](https://py-pdf.github.io/fpdf2/)|Generación de informes PDF|
|[openpyxl / xlsxwriter](https://openpyxl.readthedocs.io/)|Exportación a Excel|
|[pytest](https://pytest.org/)|Tests unitarios y de integración|
|`fhecor\_structuralcodes`|Librería interna FHECOR con funciones de verificación normativa|

\---

## Instalación y puesta en marcha

### Requisitos previos

* Python 3.11 o superior
* Node.js 18+ (requerido por Reflex para el frontend)

### Pasos

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd structural\_app

# 2. Crear y activar entorno virtual
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\\Scripts\\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Inicializar Reflex (solo la primera vez)
reflex init

# 5. Arrancar la aplicación en modo desarrollo
reflex run
```

La aplicación estará disponible en `http://localhost:3000`.

\---

## Cómo añadir un nuevo formulario

1. **Crear la carpeta** `structural\_app/forms/<nombre\_formulario>/`.
2. **Crear `config.json`** con la definición del formulario. La estructura mínima es:

```json
{
  "form\_key": "nombre\_formulario",
  "title": "Título visible en la UI",
  "description": "Descripción breve para el buscador",
  "tabs": \[
    {
      "id": "datos",
      "label": "Datos",
      "num\_columns": 2,
      "groups": \[
        {
          "type": "group",
          "id": "geometria",
          "name": "Geometría",
          "column": 1,
          "fields": \[
            { "id": "h", "label": "Altura", "symbol": "h", "unit": "m", "type": "number", "default": 3.0 }
          ]
        }
      ]
    }
  ],
  "features": { "svg": false, "viewer\_3d": false, "sketch": false }
}
```

3. **(Opcional) Crear `adapter.py`** si se necesita lógica de cálculo personalizada:

```python
from structural\_app.shared.domain.result\_models import SolverResponse, CheckResult

def calculate\_element(payload: dict) -> SolverResponse:
    h = payload.get("h", 0.0)
    ok = h > 0
    return SolverResponse(
        is\_ok=ok,
        summary="Verificación completada",
        checks=\[
            CheckResult(description="Altura positiva", status=ok, value=h, limit=0.0, unit="m")
        ]
    )
```

4. **Reiniciar la aplicación**. El `FormRegistry` descubre los formularios automáticamente y registra la nueva ruta `/<nombre-formulario>`.

> Si no se crea `adapter.py`, el motor universal intentará resolver la lógica a partir de la clave `"logic"` del `config.json`, que debe apuntar a una función de la librería `fhecor\_structuralcodes`.

\---

## Módulos principales

### `core/base\_state.py` — Estado global

`BaseState` hereda de `rx.State` y centraliza todo el estado de la aplicación:

* **`form\_data`** — Diccionario con los valores actuales del formulario.
* **`results`** — Objeto `SolverResponse` con las comprobaciones del último cálculo.
* **`calculate()`** — Lanza el cálculo. Usa `HashService` para evitar recalcular si los datos no han cambiado.
* **`set\_current\_form(key)`** — Inicializa el estado al navegar a un formulario: resetea datos, carga valores por defecto del `config.json` y activa la primera pestaña.
* **`navigate\_to\_form(key)`** / **`navigate\_to\_index()`** — Navegación programática entre páginas.
* **`load\_session(files)`** — Carga un JSON de sesión; si es de otro formulario, redirige automáticamente.

### `core/form\_registry.py` — Registro de formularios

`discover\_forms()` escanea `structural\_app/forms/` al arrancar la aplicación y carga cada `config.json` en el diccionario `FORM\_REGISTRY`. Los formularios cuya carpeta empieza por `\_` o `.` se ignoran.

### `core/solver\_dispatcher.py` — Despachador de cálculo

Jerarquía de resolución para cada llamada a `calculate()`:

1. Si existe `adapter.py` con la función `calculate\_element` → se usa el adaptador.
2. Si no → se ejecuta el **motor automático universal** (`execute\_auto\_logic`), que:

   * Carga la función de cálculo indicada en `config.json > logic.function` desde la librería `fhecor\_structuralcodes`.
   * Aplica valores por defecto inteligentes (ej. calcula `Ac` a partir de `bw` y `h`).
   * Filtra el payload para enviar solo los parámetros que la función acepta.
   * Construye los `CheckResult` a partir de la sección `logic.outputs` del JSON.

### `shared/domain/result\_models.py` — Modelos de resultado

```python
class CheckResult(BaseModel):
    description: str   # Texto de la comprobación
    status: bool       # True = CUMPLE
    value: float       # Valor calculado
    limit: float       # Valor límite normativo
    unit: str          # Unidad (kN, MPa, m…)
    ratio: float       # Relación valor/límite

class SolverResponse(BaseModel):
    is\_ok: bool              # Resultado global (todas las comprobaciones superadas)
    summary: str             # Mensaje resumen
    checks: List\[CheckResult]
    plot\_data: Optional\[dict] # Datos para la gráfica Plotly (serializado como dict)
    form\_data\_updates: Optional\[dict] # Campos a actualizar en el formulario tras el cálculo
```

### `shared/services/plot\_engine.py` — Motor de gráficas

`PlotEngine` proporciona métodos estáticos para crear y estilizar figuras Plotly con el diseño corporativo de FHECOR. Los adaptadores pueden usar `PlotEngine.apply\_standard\_layout()` para obtener un `dict` serializable compatible con Reflex.

\---

## Exportación de resultados

El flujo de exportación sigue siempre el mismo patrón:

```
BaseState.export\_\*\_to\_server()
    → ExportPayloadService.create\_report\_data()   # Prepara el dict con inputs y resultados
    → PDFExportProvider / ExcelExportProvider      # Genera el archivo
    → SessionIO.resolve\_path()                     # Resuelve la ruta de destino
```

* **PDF** — Generado con `FPDF2`. Incluye portada con información del proyecto, tabla de inputs agrupados y tabla de comprobaciones normativas con semáforo de colores.
* **Excel** — Estructura similar al PDF, exportada en formato `.xlsx`.
* El usuario puede especificar nombre de archivo y ruta desde la interfaz. La palabra clave `descargas` / `downloads` se resuelve automáticamente a la carpeta de Descargas del sistema.

\---

## Gestión de sesión

Los proyectos se pueden guardar y cargar como archivos JSON:

* **Guardar** — `BaseState.save\_session()` serializa `form\_data` junto con metadatos de control de versión (`timestamp`, `app\_version`, `hash`) y lo escribe en disco.
* **Cargar** — `BaseState.load\_session(files)` lee el JSON subido por el usuario. Si el archivo pertenece a un formulario diferente al activo, la app redirige automáticamente a la ruta correcta y lanza el cálculo.

\---

## Tests

Los tests están en `structural\_app/tests/` y siguen la misma estructura que `forms/`:

```
tests/
├── forms/
│   ├── muro/
│   │   ├── test\_adapter.py    # Prueba la función calculate\_element del adaptador
│   │   └── test\_state.py
│   └── ...
└── shared/
    └── test\_hash\_service.py
```

Para ejecutar los tests:

```bash
pytest structural\_app/tests/ -v
```

Los tests del adaptador usan `pytest-asyncio` para los eventos asíncronos de Reflex.

\---

## Convenciones y estilo de código

* **Formularios**: una carpeta por formulario en `forms/`, siempre con `config.json`. El `adapter.py` es opcional.
* **Rutas URL**: se derivan automáticamente de la clave del formulario reemplazando `\_` por `-` (ej. `cortante\_circular` → `/cortante-circular`).
* **Estado**: toda la lógica de UI y de negocio pasa por `BaseState`. Los componentes no mantienen estado propio.
* **Serialización**: los datos de Plotly se serializan siempre a `dict` mediante `fig.to\_json()` antes de asignarse al estado, para evitar incompatibilidades con tipos NumPy.
* **Hash de cálculo**: `HashService.compute\_hash(form\_data)` evita relanzar el solver si el usuario pulsa Calcular sin cambiar ningún dato.
* **Estilo visual**: fuente corporativa `Lato`, color primario `rgb(0, 50, 100)`.

