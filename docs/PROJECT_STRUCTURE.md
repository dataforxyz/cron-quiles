# Estructura del Proyecto

```
cron-quiles/
├── .github/
│   ├── workflows/
│   │   ├── update-events.yml      # GitHub Actions workflow
│   │   └── README.md               # Documentación del workflow
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md           # Template para reportar bugs
│   │   └── feature_request.md      # Template para solicitar features
│   ├── PULL_REQUEST_TEMPLATE.md    # Template para PRs
│   └── dependabot.yml              # Configuración de Dependabot
│
├── .gitignore                       # Archivos a ignorar en Git
│
├── LICENSE                          # Licencia MIT
├── README.md                        # Documentación principal
├── CONTRIBUTING.md                  # Guía para contribuidores
├── CHANGELOG.md                     # Historial de cambios
│
├── src/
│   └── cronquiles/                  # Paquete Python principal
│       ├── __init__.py             # Inicialización del paquete
│       ├── main.py                 # CLI principal
│       ├── ics_aggregator.py       # Lógica de agregación y deduplicación
│       └── google_calendar.py      # Publicación en Google Calendar
│
├── config/                          # Archivos de configuración
│   ├── feeds.yaml                  # Configuración de feeds (YAML)
│   └── list_icals.txt              # Lista alternativa de feeds (texto)
│
├── docs/                            # Documentación adicional
│   ├── AGENTS.md                   # Especificaciones del proyecto
│   └── PROJECT_STRUCTURE.md        # Este archivo
│
├── examples/                        # Ejemplos y scripts de demostración
│   └── example_event.py            # Ejemplo de formato de eventos
│
├── main.py                          # Punto de entrada CLI (raíz)
├── requirements.txt                # Dependencias Python
├── pyproject.toml                   # Configuración del proyecto (PEP 518)
│
├── gh-pages/                        # Archivos para GitHub Pages
│   ├── index.html                  # Página principal con calendario embebido
│   ├── cronquiles.ics              # Calendario ICS unificado (generado)
│   ├── cronquiles.json             # JSON con eventos (generado)
│   ├── serve.py                    # Servidor HTTP para desarrollo local
│   ├── serve.sh                    # Script para iniciar servidor local
│   └── README-LOCAL.md             # Guía para desarrollo local
│
└── [Archivos generados - obsoletos en raíz]
    # Nota: Los archivos ahora se generan en gh-pages/
```

## Descripción de Directorios

### `src/cronquiles/`
Código fuente principal del proyecto. Contiene:
- **`__init__.py`**: Inicialización del paquete Python
- **`main.py`**: CLI principal con argumentos y lógica de ejecución
- **`ics_aggregator.py`**: Módulo con clases `EventNormalized` e `ICSAggregator`
  - `EventNormalized`: Normaliza eventos, detecta online/presencial, extrae grupo/ubicación, formatea títulos
  - `ICSAggregator`: Agrega múltiples feeds ICS, deduplica eventos, genera ICS/JSON
- **`google_calendar.py`**: Publicación de eventos en Google Calendar (opcional)

### `config/`
Archivos de configuración:
- **`feeds.yaml`**: Configuración principal de feeds ICS (formato YAML)
- **`list_icals.txt`**: Lista alternativa de feeds (formato texto plano, una URL por línea)

### `docs/`
Documentación adicional del proyecto:
- **`AGENTS.md`**: Especificaciones originales y requisitos del proyecto
- **`PROJECT_STRUCTURE.md`**: Este archivo con la estructura del proyecto

### `examples/`
Ejemplos y scripts de demostración:
- **`example_event.py`**: Script que muestra el formato de eventos en diferentes representaciones

### Raíz del Proyecto
- **`main.py`**: Punto de entrada principal que permite ejecutar desde la raíz
- **`requirements.txt`**: Lista de dependencias Python
- **`pyproject.toml`**: Configuración del proyecto según PEP 518
- **`README.md`**: Documentación principal
- **`LICENSE`**: Licencia MIT
- **`CONTRIBUTING.md`**: Guía para contribuidores
- **`CHANGELOG.md`**: Historial de cambios

### `.github/`
Configuración de GitHub:
- **`workflows/`**: Workflows de GitHub Actions
- **`ISSUE_TEMPLATE/`**: Templates para crear issues
- **`PULL_REQUEST_TEMPLATE.md`**: Template para pull requests
- **`dependabot.yml`**: Configuración de Dependabot

## Archivos Generados

Estos archivos se generan al ejecutar `main.py` y se suben al repo automáticamente por GitHub Actions:
- **`gh-pages/cronquiles.ics`**: Calendario ICS unificado con eventos formateados
- **`gh-pages/cronquiles.json`**: JSON con eventos (si se usa `--json`)
  - Los eventos incluyen títulos formateados: `Grupo|Nombre evento|Online` o `Grupo|Nombre evento|País|Estado`

**Nota:** Los archivos se generan directamente en `gh-pages/` para publicación en GitHub Pages.

## GitHub Pages

La carpeta `gh-pages/` contiene todos los archivos necesarios para GitHub Pages:
- **`index.html`**: Página principal con diseño terminal y calendario embebido
- **`cronquiles.ics`**: Calendario ICS para descarga y suscripción WebCal
- **`cronquiles.json`**: Datos JSON para uso programático
- **`serve.py`** / **`serve.sh`**: Scripts para probar el sitio localmente
- **`README-LOCAL.md`**: Instrucciones para desarrollo local

## Uso de la Estructura

### Ejecutar desde la raíz
```bash
python main.py
```

### Ejecutar el módulo directamente
```bash
python -m src.cronquiles.main
```

### Importar como paquete
```python
from src.cronquiles import ICSAggregator
```

**Nota:** El paquete Python se llama `cronquiles` (sin guión) para cumplir con las convenciones de nombres de paquetes Python.

## Ventajas de esta Estructura

1. **Organización clara**: Separación entre código, configuración, documentación y ejemplos
2. **Escalabilidad**: Fácil agregar más módulos o subpaquetes
3. **Estándar Python**: Sigue convenciones comunes de proyectos Python
4. **Mantenibilidad**: Fácil encontrar y modificar archivos
5. **Distribución**: Listo para empaquetar con `setuptools` o `pip`
