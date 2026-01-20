# CLAUDE.md

Este archivo proporciona orientación para Claude Code (claude.ai/code) al trabajar con código en este repositorio.

## Descripción General del Proyecto

Cron-Quiles es una herramienta Python que agrega calendarios de eventos tech de múltiples fuentes (Meetup, Luma, Eventbrite, feeds ICS) en calendarios unificados y deduplicados para México. Se ejecuta automáticamente a través de GitHub Actions cada 6 horas.

## Comandos Comunes

```bash
# Instalación
make install-dev  # Instala prod + dev
make install      # Solo producción

# Ejecutar pipeline
make run-all                                    # Todas las ciudades
make run ARGS="--city cdmx --json"             # Ciudad específica
make run ARGS="--all-cities --output-dir out/"  # Custom output

# Tests
make test                                  # Todos
make test-file FILE=test_ics_aggregator.py # Específico
make test-filter FILTER="normalize_title"  # Filtrado

# Linting y formateo
make lint          # Verifica
make format        # Formatea
make format-check  # Verifica sin cambiar

# Servidor local
make serve  # http://localhost:8000

# Herramientas
make tools-deduplicate
make tools-populate-cache
make tools-scan-feeds
make tools-scrape-meetup

# Gestión
make clean   # Limpia archivos generados
make update  # Actualiza dependencias
make check   # Verifica entorno

# Ver todos los comandos
make help
```

## Gestión de Dependencias con uv

### Instalación de uv

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Uso Básico

```bash
# Instalar desde lockfile
uv sync --frozen

# Con extras de desarrollo
uv sync --frozen --all-extras

# Agregar dependencia
uv add requests
uv add --dev pytest

# Actualizar
uv lock --upgrade-package requests  # Específica
uv lock --upgrade                   # Todas
```

## Arquitectura

### Core Pipeline (`src/cronquiles/`)

- **`main.py`**: CLI entry point con argument parsing. Carga feeds desde `config/feeds.yaml`, orquesta agregación y genera archivos de salida.
- **`ics_aggregator.py`**: Clase `ICSAggregator` - el orquestador principal. Despacha a agregadores específicos basándose en patrones de URL, maneja deduplicación, geocodificación y gestión de historial.
- **`models.py`**: Clase `EventNormalized` - normaliza eventos de diferentes fuentes en un formato unificado. Maneja limpieza de títulos, extracción de tags, conversión de zonas horarias y generación de claves hash para deduplicación.
- **`history_manager.py`**: Persiste eventos en `data/history.json` para preservación de datos históricos y lógica de fusión.

### Agregadores (`src/cronquiles/aggregators/`)

Cada agregador extrae eventos de un tipo específico de fuente:
- `ics.py`: Parser genérico de feeds ICS (implementación base)
- `meetup.py`: Extracción específica de Meetup con enriquecimiento JSON-LD para ubicaciones
- `luma.py`: Integración de calendario Luma con limpieza de URLs
- `eventbrite.py`: Soporte de organizador Eventbrite y evento único
- `manual.py`: Inyección manual de eventos basada en JSON desde `config/manual_events.json`

### Lógica de Enrutamiento de Fuentes

El método `ICSAggregator.aggregate_feeds()` enruta URLs a agregadores:
- URLs `eventbrite.com` → EventbriteAggregator
- URLs `lu.ma` o `luma.com` → LumaAggregator
- URLs `meetup.com` → MeetupAggregator
- Todo lo demás → GenericICSAggregator

### Deduplicación

Los eventos se deduplicaban usando claves hash basadas en el título normalizado + bloque de tiempo (tolerancia de 2 horas en UTC). Cuando se encuentran duplicados, se mantiene la mejor versión (prefiriendo eventos con URLs y descripciones más largas) y se fusionan URLs alternativas en la descripción.

### Generación de Salida

Los archivos se generan en `gh-pages/data/`:
- `cronquiles-mexico.ics/json` - Calendario unificado nacional
- `cronquiles-{state-code}.ics/json` - Calendarios por estado (ej: `cronquiles-mx-cmx.ics`)
- `cronquiles-online.ics/json` - Solo eventos en línea
- `states_metadata.json` - Manifest del frontend con info de estados

### Filtrado por País

Solo se procesan eventos en México (`country_code == "MX"`) o eventos En línea. Los eventos fuera de México se filtran.

## Archivos Clave

- `config/feeds.yaml`: Lista de todas las fuentes de feeds con URLs, nombres y descripciones
- `config/manual_events.json`: Entradas de eventos manuales (opcional)
- `data/history.json`: Base de datos de historial de eventos persistente
- `data/geocoding_cache.json`: Resultados de geocodificación en caché para evitar límites de API

## Directorio de Herramientas

Scripts de mantenimiento en `tools/`:
- `scrape_meetup_history.py`: Extraer eventos históricos de Meetup
- `populate_cache_from_history.py`: Pre-popular caché de geocodificación
- `scan_feeds_and_cache.py`: Escanear feeds y asegurar completitud de caché
- `update_communities_status.py`: Actualizar estado de comunidad en docs

## Requisitos de Documentación

Al realizar cambios:
1. Actualizar `CHANGELOG.md` con los cambios
2. Actualizar `docs/COMMUNITIES.md` si se agregan nuevos feeds a `config/feeds.yaml`
3. Mantener docstrings e comentarios en línea actuales
4. No commitear archivos generados en `gh-pages/data/` manualmente (GitHub Actions se encarga)

## Estilo de Código

- Python 3.10+
- Black para formateo
- Flake8 para linting (máximo 127 caracteres por línea)
- Type hints recomendados
- Docstrings para módulos, clases y funciones públicas
- **Todos los comentarios y documentación de código deben estar en español**
- Las cadenas visibles para el usuario deben estar en español (ej: "Ver en Meetup" no "View on Meetup")
