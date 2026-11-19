import { useState } from 'react';

export function RadarPilot() {
  const [result, setResult] = useState<unknown>(null);
  const [working, setWorking] = useState(false);

  async function run() {
    setWorking(true);
    try {
      const response = await fetch('/api/radar-pilot');
      setResult(await response.json());
    } catch (error) {
      setResult({ error: error instanceof Error ? error.message : String(error) });
    } finally {
      setWorking(false);
    }
  }

  return (
    <main style={{ fontFamily: 'system-ui', padding: 16 }}>
      <h1>RadarIsma · Devvit</h1>
      <p>Prueba de lectura de r/ChatGPT y r/sysadmin. No guarda ni exporta datos.</p>
      <button onClick={run} disabled={working}>
        {working ? 'Consultando…' : 'Probar lectura'}
      </button>
      <pre style={{ whiteSpace: 'pre-wrap', overflowWrap: 'anywhere', fontSize: 12 }}>
        {result ? JSON.stringify(result, null, 2) : 'Sin consultar todavía'}
      </pre>
    </main>
  );
}
