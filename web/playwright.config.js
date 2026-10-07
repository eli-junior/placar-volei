// Suíte de navegador (CV4.DS3.TS1). Ferramenta de desenvolvimento: não entra
// na imagem de runtime. Sobe o FastAPI com o build estático e um SQLite
// descartável; nunca aponta para o banco de produção.
import { defineConfig, devices } from '@playwright/test';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const PORTA = 8799;
const banco = join(tmpdir(), `placar-e2e-${Date.now()}.db`);

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [['list']],
  use: {
    baseURL: `http://127.0.0.1:${PORTA}`,
    trace: 'retain-on-failure',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: {
    command: `uv run uvicorn app.main:app --host 127.0.0.1 --port ${PORTA}`,
    cwd: '..',
    url: `http://127.0.0.1:${PORTA}/health`,
    reuseExistingServer: false,
    timeout: 60_000,
    // Cada teste cria a própria sala; o limite de produção (20) não serve aqui.
    env: { DB_PATH: banco, GERENCIADOR_DB_PATH: banco.replace('.db', '-gerenciador.db'), OWNER_SECRET: 'segredo-e2e', WATCH_AUTO_GRANT: 'eli', MAX_QUADRAS: '500' },
  },
});
