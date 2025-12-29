# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Added
- **Interfaz web mejorada con diseño terminal** (nuevo)
  - Diseño estilo terminal consistente con shellaquiles-org
  - Calendario mensual visual embebido con eventos del mes
  - Navegación entre meses con botones anterior/siguiente
  - Visualización automática de todos los eventos del mes actual
  - Indicadores visuales de días con eventos
  - Estilo responsive optimizado para móvil y escritorio
- **Estructura mejorada para GitHub Pages** (nuevo)
  - Archivos movidos a carpeta `gh-pages/` para mejor organización
  - Scripts de desarrollo local (`serve.py`, `serve.sh`)
  - Documentación para desarrollo local (`README-LOCAL.md`)
- **Mejoras en la interfaz web** (nuevo)
  - Detección automática de errores en desarrollo local con mensajes útiles
  - Mejor manejo de errores con instrucciones claras
  - Interfaz más limpia y enfocada

### Changed
- **Reorganización de archivos** (cambio)
  - Archivos generados (`cronquiles.ics`, `cronquiles.json`) ahora se generan en `gh-pages/`
  - Workflow de GitHub Actions actualizado para generar archivos directamente en `gh-pages/`
  - `.gitignore` actualizado para reflejar nueva estructura
- **Interfaz web** (cambio)
  - Diseño completamente renovado con tema terminal
  - Calendario visual reemplaza lista de próximos eventos
  - Mejor experiencia de usuario con información más accesible

### Fixed
- Corregido problema de codificación de caracteres (acentos) en eventos ICS
  - Los caracteres con acentos ahora se muestran correctamente (ej: "Cariño" en lugar de "CariÃ±o")
  - Implementada función `fix_encoding()` para corregir problemas de mojibake automáticamente

### Added (versiones anteriores)
- Agregador de feeds ICS públicos
- Normalización de eventos (título, fecha, ubicación, etc.)
- Deduplicación inteligente de eventos similares
- Tags automáticos por keywords (Python, AI, Cloud, DevOps, etc.)
- Generación de calendario ICS unificado
- Generación opcional de JSON con eventos
- CLI con múltiples opciones de configuración
- GitHub Actions workflow para actualización automática
- Manejo robusto de timezones
- Tolerancia a feeds caídos sin romper el proceso
- **Publicación directa en Google Calendar** (nuevo)
  - Soporte para autenticación OAuth2
  - Publicación automática de eventos
  - Modo dry-run para pruebas
  - Soporte para calendarios personalizados
- **Publicación automática en GitHub Pages** (nuevo)
  - Los archivos ICS y JSON se publican automáticamente
  - Página web con interfaz para descargar/suscribir
  - Soporte para suscripción WebCal
  - Actualización automática cada 6 horas

### Changed
- (Ningún cambio aún)

### Fixed
- (Ningún fix aún)

### Removed
- (Nada removido aún)

---

## [1.0.0] - 2024-01-XX

### Added
- Versión inicial del proyecto
- Soporte para múltiples feeds ICS (Meetup, Luma)
- Sistema de deduplicación basado en título normalizado + fecha
- Detección automática de tags
- Documentación completa en README.md
- Ejemplos de configuración

[Unreleased]: https://github.com/shellaquiles/cron-quiles/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/shellaquiles/cron-quiles/releases/tag/v1.0.0
