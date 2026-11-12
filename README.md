# RadarIsma — recopilación verificable de Reddit

Este proyecto separa la **recopilación** de Reddit de la selección editorial y del PDF.

## Requisitos

- Python 3.10 o superior; no requiere paquetes externos.
- **Autorización de Reddit** para usar su Data API. No ejecutes el recopilador contra Reddit hasta obtenerla.
- Credenciales `REDDIT_CLIENT_ID` y `REDDIT_CLIENT_SECRET` de una aplicación que permita el flujo OAuth de aplicación (`client_credentials`). El flujo definitivo dependerá de lo que apruebe Reddit.
- Un `REDDIT_USER_AGENT` identificable, por ejemplo `script:reddit-radar:0.1 (by /u/TU_USUARIO)`.

No incorpora técnicas para saltarse bloqueos ni utiliza servicios de scraping.

## Uso

En PowerShell, **una vez autorizado el acceso**:

```powershell
$env:REDDIT_CLIENT_ID = 'TU_ID'
$env:REDDIT_CLIENT_SECRET = 'TU_SECRETO'
$env:REDDIT_USER_AGENT = 'script:reddit-radar:0.1 (by /u/TU_USUARIO)'
python .\collect.py --days 7 --comments 20
```

El script crea `output/reddit_YYYY-MM-DD.json`, `output/reddit_YYYY-MM-DD.csv` y `output/coverage_YYYY-MM-DD.json`. Por defecto usa los últimos 7 días en UTC; puedes fijar la fecha de corte con `--end-date YYYY-MM-DD` (incluye ese día UTC). Para una edición semanal consistente, fija `--end-date`.

## Qué verifica

- Recorre **las 19 comunidades solicitadas**, sin sustituir una por otra.
- Obtiene listados recientes y populares; filtra por fecha y subreddit exacto.
- Elimina duplicados por ID, conserva enlaces directos y métricas disponibles.
- Recupera una muestra de comentarios principales (si está permitido), sin presentarla como consenso exhaustivo.
- Genera un archivo de cobertura por comunidad con recuentos, errores y estado.
- Si falla una comunidad, lo informa: **no declara que no hubo publicaciones**.

## Límites

- La API puede no estar disponible para esta cuenta o aplicación; errores 401/403/429 pueden impedir la consulta.
- Los listados tienen límites de paginación; `--pages` controla cuántas páginas revisar por ordenación. La ausencia de resultados no prueba ausencia de actividad.
- `score`, `num_comments` y votos son instantáneas, no estadísticas históricas.
- Los comentarios recuperados son una muestra y no incluyen necesariamente todas las respuestas anidadas.
- El prototipo no implementa todavía controles automáticos de retención y eliminación de datos. **Estos deben implementarse antes del uso operativo**, conforme a las condiciones de autorización de Reddit.
- No envíes información confidencial, tokens ni credenciales al chat. Mantén secretos fuera de GitHub.

## Siguiente etapa

Usar el JSON como entrada de una revisión editorial: seleccionar 1–3 hilos útiles por comunidad cuando haya evidencia, comprobar contenido y comentarios, y generar el PDF. No automatizar resúmenes de publicaciones que no se hayan podido leer.

## Estado y pruebas

**Prototipo sin acceso a la API validado:** el código supera tres pruebas locales sin red; no se ha comprobado todavía una sesión real con Reddit. Su funcionamiento depende de la autorización de Reddit y de que el flujo OAuth seleccionado sea aceptado para la aplicación aprobada.

Ejecutar pruebas locales:

```powershell
python -m unittest discover -s tests -v
```

No subas secretos ni archivos de salida al repositorio. Este proyecto **no** incluye publicación automática de informes, inteligencia artificial, entrenamiento de modelos ni procesamiento de datos personales. Antes de añadir modelos de IA o distribuir datos de Reddit, comprueba que lo permitan la autorización recibida y las condiciones vigentes.

Repositorio destinado a respaldar una **solicitud de acceso**, no prueba de que Reddit haya autorizado la aplicación.
