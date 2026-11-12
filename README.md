# RadarIsma

Quiero seguir lo más interesante de Reddit sin depender únicamente de lo que encuentran los buscadores. Por eso empecé RadarIsma: un pequeño programa en Python que reúne publicaciones de 19 comunidades que sigo y deja la información organizada para preparar mis informes semanales en español.

El proyecto es personal, sin fines comerciales y todavía está en desarrollo.

## ¿Qué hace por ahora?

- Consulta los apartados **new** y **top** de los 19 subreddits definidos en `collect.py`.
- Filtra las publicaciones por fecha y por comunidad.
- Guarda el título, el contenido disponible, la fecha, el enlace directo, la puntuación (`score`) y el número de comentarios (`num_comments`).
- Puede recuperar una muestra de comentarios públicos de algunos hilos. No equivale a leer toda la conversación.
- Descarta publicaciones duplicadas por ID y omite los mensajes fijados.
- Exporta los resultados a **JSON** y **CSV**, junto con un archivo que indica qué se pudo consultar y dónde hubo errores.

La idea es usar después estos datos para seleccionar buenas discusiones, leerlas con más cuidado y preparar el informe en PDF. **Esa parte editorial todavía no está automatizada.**

## Comunidades incluidas

`r/ArtificialInteligence`, `r/ChatGPT`, `r/ClaudeAI`, `r/CompTIA`, `r/DeepSeek`, `r/Futurology`, `r/GeminiAI`, `r/GoogleAIStudio`, `r/MistralAI`, `r/OpenAI`, `r/PromptEngineering`, `r/antiai`, `r/claude`, `r/filen_io`, `r/opensource`, `r/perplexity_ai`, `r/singularity`, `r/sysadmin` y `r/vibecoding`.

## Antes de usarlo

Necesitas **Python 3.10 o superior**. No hay que instalar bibliotecas adicionales: el programa utiliza la biblioteca estándar de Python.

También necesitas que **Reddit autorice el uso de su Data API**. La solicitud está pendiente, así que aún no he comprobado el funcionamiento del programa con una conexión real a Reddit.

El prototipo utiliza OAuth con el flujo `client_credentials`. Para ejecutarlo tendrás que configurar `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET` y un `REDDIT_USER_AGENT` identificable. El acceso y el flujo disponibles dependerán de la autorización que conceda Reddit.

No compartas las credenciales ni las subas a GitHub.

## Cómo ejecutarlo

Una vez que tengas acceso autorizado, abre PowerShell en la carpeta del proyecto y configura estas variables:

```powershell
$env:REDDIT_CLIENT_ID = 'TU_ID'
$env:REDDIT_CLIENT_SECRET = 'TU_SECRETO'
$env:REDDIT_USER_AGENT = 'script:reddit-radar:0.1 (by /u/TU_USUARIO)'

python .\collect.py --days 7 --comments 20
```

Por defecto, `--days 7` toma los últimos siete días en **UTC**. Si quieres cerrar el informe en una fecha concreta, usa `--end-date YYYY-MM-DD`, por ejemplo:

```powershell
python .\collect.py --days 7 --end-date 2026-11-12 --comments 20
```

En ese caso, la fecha indicada se incluye completa en UTC. También puedes ajustar la búsqueda con `--pages` y limitar los hilos cuyos comentarios se consultan con `--max-comment-posts`.

El programa crea estos archivos dentro de `output/`:

- `reddit_YYYY-MM-DD.json`: publicaciones y muestras de comentarios.
- `reddit_YYYY-MM-DD.csv`: datos principales para revisar o filtrar.
- `coverage_YYYY-MM-DD.json`: resultados de consulta por comunidad, incluidos los errores.

La carpeta `output/` está excluida de Git mediante `.gitignore`.

## Lo que todavía hay que resolver

Prefiero dejar claros los límites desde el principio:

- **No garantiza una recopilación completa.** Reddit limita la paginación y la disponibilidad de sus listados. Que no aparezca un hilo no significa que no exista.
- **Los comentarios son una muestra.** Algunas respuestas anidadas pueden quedar fuera; no sirve para afirmar que toda una comunidad piensa igual.
- **Las métricas son instantáneas.** `score` y `num_comments` pueden cambiar después de la consulta.
- **Puede fallar el acceso.** Errores HTTP `401`, `403` o `429`, entre otros, pueden impedir recuperar información. Esos fallos deben revisarse en el archivo de cobertura.
- **Faltan controles de conservación y borrado de datos.** Tendré que implementarlos antes de utilizar el sistema de forma habitual y de acuerdo con las condiciones que establezca Reddit.

No hay funciones para publicar, votar, enviar mensajes o modificar cuentas. Tampoco se intenta eludir las restricciones de acceso de Reddit.

## Pruebas

El repositorio incluye tres pruebas que no necesitan conexión ni credenciales. Puedes ejecutarlas así:

```powershell
python -m unittest discover -s tests -v
```

Estas pruebas comprueban la lista de comunidades, la preparación de la solicitud OAuth y el filtrado básico de comentarios. **No sustituyen una prueba real con la API de Reddit.**

## Qué sigue

Primero necesito obtener la autorización de Reddit y comprobar que el recopilador puede leer publicaciones y comentarios correctamente. Después tocará mejorar la cobertura, fijar las reglas de conservación de datos y preparar la selección editorial y el PDF.

Los datos recopilados no se utilizarán para entrenar modelos. Si más adelante incorporo resúmenes asistidos por IA, revisaré antes que ese uso esté permitido por la autorización y las condiciones de Reddit.

Este repositorio acompaña una **solicitud de acceso a la Data API**; que el código esté publicado no significa que Reddit ya haya aprobado su uso.
