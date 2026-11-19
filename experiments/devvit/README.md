# Prueba Devvit de RadarIsma

Esta prueba intenta responder una sola pregunta: **¿puede una aplicación Devvit de pruebas leer publicaciones y algunos comentarios de r/ChatGPT y r/sysadmin, sin instalarse en esas comunidades?**

No pretende generar el informe semanal ni trasladar datos a Python. El experimento se ejecuta **dentro de Reddit**: no conserva datos, no hace peticiones HTTP externas y no envía contenido a modelos de IA.

## Preparar el entorno

1. Instala Node.js **24.18.0 o superior**, según el [inicio rápido de Reddit](https://developers.reddit.com/docs/quickstart).
2. Entra a [developers.reddit.com/new](https://developers.reddit.com/new) con tu cuenta y crea una aplicación de pruebas utilizando la plantilla **React**. El asistente te indicará los comandos que debes ejecutar en tu PC.
3. Abre el proyecto creado, no la carpeta del recopilador Python. Devvit es un proyecto independiente, con su propio `devvit.json` y dependencias.

## Incorporar la prueba

En el proyecto **React generado por Reddit**:

- Copia `pilot-route.ts` a `src/server/routes/radar-pilot.ts`.
- Copia `pilot-panel.tsx` a `src/client/radar-pilot.tsx`.
- En `src/server/index.ts`, añade el import:
  ```ts
  import { radarPilot } from './routes/radar-pilot';
  ```
  Y registra la ruta junto a las existentes:
  ```ts
  app.route('/api', radarPilot);
  ```
- En `src/client/game.tsx`, puedes reemplazar temporalmente el contenido generado por:
  ```tsx
  import { StrictMode } from 'react';
  import { createRoot } from 'react-dom/client';
  import { RadarPilot } from './radar-pilot';

  createRoot(document.getElementById('root')!).render(
    <StrictMode><RadarPilot /></StrictMode>
  );
  ```
- Dentro del `devvit.json` que genera Reddit, **conserva el resto de su configuración** y asegúrate de habilitar:
  ```json
  "permissions": {
    "reddit": { "enable": true }
  }
  ```

Sigue las instrucciones del asistente y ejecuta `npm run dev` dentro de la carpeta de la aplicación Devvit. Abre la URL de playtest, entra al post de prueba y selecciona **Launch App**; pulsa **Probar lectura**.

No publiques ni solicites la revisión pública de la aplicación: primero debemos comprobar el resultado en el subreddit de prueba que Devvit crea para ti.

## Qué esperamos encontrar

- Si ambos subreddits devuelven publicaciones fechadas dentro de los últimos siete días, con enlaces directos, la **lectura entre comunidades** funciona.
- Si también aparecen muestras de comentarios, se confirma esa parte de la API.
- Si devuelve `status: error`, copia el mensaje sin incluir tokens ni credenciales. Un error significa que la prueba necesita diagnóstico, no que la comunidad estuvo inactiva.
- Si devuelve `status: ok` con `posts: []`, **no implica que la comunidad carezca de actividad**. Esta prueba solo consulta los 20 posts más nuevos de cada subreddit y filtra los de los últimos siete días.

## Qué queda sin resolver

**Un resultado favorable no autoriza exportar datos.** Reddit exige respetar sus [Devvit Rules](https://developers.reddit.com/docs/devvit_rules), incluidos límites sobre almacenamiento, eliminación, usos externos y servicios de IA. Los [External Endpoints](https://developers.reddit.com/docs/capabilities/server/external-endpoints) también requieren acceso adicional. No habilitaremos ninguna exportación ni procesamiento externo sin confirmar expresamente que el uso esté permitido.

El recopilador Python original **no cambia** y sigue sin tener autorización de la Data API externa.

Código **preparado, aún no probado en Devvit real**. Necesita que el usuario cree la app con la plantilla de Reddit y ejecute el playtest.
