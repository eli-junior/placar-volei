import { test as base } from '@playwright/test';

// `abrir(opções)` cria um cliente isolado (cookie próprio) e o fecha ao fim
// do teste; sem isso os WebSockets de testes anteriores se acumulam.
export const test = base.extend({
  abrir: async ({ browser }, usar) => {
    const contextos = [];
    await usar(async (opcoes = {}, iniciar) => {
      const ctx = await browser.newContext(opcoes);
      if (iniciar) await ctx.addInitScript(iniciar.fn, iniciar.arg);
      contextos.push(ctx);
      return ctx.newPage();
    });
    await Promise.all(contextos.map((c) => c.close()));
  },
});
export { expect } from '@playwright/test';

// Apoio da suíte de navegador: cria salas e participantes pela API real, no
// contexto do navegador, para que o cookie de sessão fique com o cliente.
export async function postar(pagina, url, corpo = {}) {
  return pagina.evaluate(async ([u, c]) => {
    const r = await fetch(u, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(c) });
    return { status: r.status, corpo: await r.json().catch(() => null) };
  }, [url, corpo]);
}

let contador = 0;
export const apelido = (base) => `${base}${++contador}${Math.random().toString(36).slice(2, 5)}`;

export async function criarSala(pagina, { nome = 'Arena', config } = {}) {
  await pagina.goto('/');
  const { status, corpo } = await postar(pagina, '/api/quadras', { apelido: apelido('Eli'), nome });
  if (status !== 201) throw new Error(`Criar sala falhou (${status}): ${JSON.stringify(corpo)}`);
  if (config) await postar(pagina, `/api/quadras/${corpo.id}/configurar`, config);
  await pagina.goto(`/quadra/${corpo.id}`);
  await pagina.getByLabel(/Marcar ponto para/).first().waitFor();
  return corpo;
}

export async function entrarNaSala(pagina, id, nome = apelido('Esp')) {
  await pagina.goto('/');
  const { corpo } = await postar(pagina, `/api/quadras/${id}/entrar`, { apelido: nome });
  await pagina.goto(`/quadra/${id}`);
  await pagina.locator('.area-resultado, .palco').first().waitFor();
  return corpo.participante ?? corpo;
}

export async function semRolagem(pagina, seletor = '.btn-marcar, .btn-desfazer, .btn-topo, .chip-codigo, .status-topo') {
  return pagina.evaluate((sel) => ({
    rolaVertical: document.documentElement.scrollHeight > innerHeight + 1,
    rolaHorizontal: document.documentElement.scrollWidth > innerWidth + 1,
    foraDaTela: [...document.querySelectorAll(sel)].filter((e) => {
      const r = e.getBoundingClientRect();
      return r.bottom > innerHeight + 1 || r.right > innerWidth + 1 || r.left < -1;
    }).length,
  }), seletor);
}

// APK (CV7.TS1/US1): Capacitor simulado e o servidor "no ar" ou "fora". O
// `/health` de outra origem precisa de CORS para o fetch do navegador lê-lo;
// no APK real o teste usa a rede nativa e não tem esse limite.
export const comCasca = { fn: (tema) => {
  window.Capacitor = { isNativePlatform: () => true };
  try { if (tema) localStorage.setItem('placar:tema', tema); } catch {}
}, arg: null };

export const servidorNoAr = (pagina) => pagina.route('**/health', (rota) => rota.fulfill({
  status: 200,
  contentType: 'application/json',
  headers: { 'access-control-allow-origin': '*' },
  body: JSON.stringify({ status: 'ok', version: 'e2e' }),
}));

export const servidorFora = (pagina) => pagina.route('**/health', (rota) => rota.abort());

/** O túnel responde, mas o backend está fora: 502 sem o corpo do /health. */
export const backendFora = (pagina) => pagina.route('**/health', (rota) => rota.fulfill({
  status: 502,
  headers: { 'access-control-allow-origin': '*' },
  body: 'Bad gateway',
}));

export const abrirCasca = (pagina, baseURL) => pagina.goto(baseURL.replace('127.0.0.1', 'localhost'));
