# GitHub Actions Workflow

Este workflow actualiza automáticamente el calendario de eventos cada 6 horas.

## ¿Qué hace?

1. Descarga todos los feeds ICS configurados
2. Normaliza y deduplica eventos
3. Genera `cronquiles.ics` y `cronquiles.json`
4. Hace commit y push automático si hay cambios

## Activación

El workflow se activa automáticamente cuando:
- Se hace push al repositorio (solo si cambian archivos relevantes)
- Cada 6 horas según el schedule
- Manualmente desde la pestaña Actions en GitHub

## Permisos necesarios

Para que el workflow pueda hacer commit y push, asegúrate de que:

1. El repositorio tenga habilitado "Allow GitHub Actions to create and approve pull requests" en Settings → Actions → General
2. O usa un Personal Access Token (PAT) con permisos de escritura en `Settings → Secrets → Actions`

## Ver logs

Ve a la pestaña **Actions** en GitHub para ver:
- Historial de ejecuciones
- Logs detallados de cada paso
- Errores si los hay
