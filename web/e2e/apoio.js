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

export async function semRolagem(pagina, seletor = '.btn-marcar, .btn-desfazer, .btn-base, .sala-header button, .ws-status') {
  return pagina.evaluate((sel) => ({
    rolaVertical: document.documentElement.scrollHeight > innerHeight + 1,
    rolaHorizontal: document.documentElement.scrollWidth > innerWidth + 1,
    foraDaTela: [...document.querySelectorAll(sel)].filter((e) => {
      const r = e.getBoundingClientRect();
      return r.bottom > innerHeight + 1 || r.right > innerWidth + 1 || r.left < -1;
    }).length,
  }), seletor);
}
