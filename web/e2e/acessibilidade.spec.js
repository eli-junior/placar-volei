// CV4.DS3.TS1 — axe nas telas reais, nos dois temas. Cobre o que o axe
// consegue medir (contraste de texto, nomes acessíveis, ARIA); não prova
// conformidade WCAG completa.
import AxeBuilder from '@axe-core/playwright';
import { test, expect, criarSala, entrarNaSala } from './apoio.js';

const TEMAS = { escuro: null, sol: 'sol' };

function comTema(abrir, tema, viewport = { width: 390, height: 844 }) {
  return abrir({ viewport }, { fn: (t) => { try { if (t) localStorage.setItem('placar:tema', t); } catch {} }, arg: tema });
}

async function analisar(pagina) {
  // Contraste medido no meio de um fade dá falso positivo: espera as animações.
  await pagina.evaluate(() => Promise.all(document.getAnimations().filter((a) => a.effect?.getTiming().iterations !== Infinity).map((a) => a.finished.catch(() => {}))));
  const { violations } = await new AxeBuilder({ page: pagina }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze();
  return violations.map((v) => `${v.id} (${v.impact}): ${v.nodes.length} × ${v.nodes[0]?.target.join(' ')}`);
}

for (const [nome, tema] of Object.entries(TEMAS)) {
  test(`home sem violações axe — tema ${nome}`, async ({ abrir }) => {
    const p = await comTema(abrir, tema);
    await p.goto('/');
    await p.waitForLoadState('networkidle');
    expect(await analisar(p)).toEqual([]);
  });

  test(`página não encontrada sem violações axe — tema ${nome}`, async ({ abrir }) => {
    const p = await comTema(abrir, tema);
    await p.goto('/rota-inexistente');
    await expect(p.getByRole('heading', { name: 'Página não encontrada' })).toBeVisible();
    expect(await analisar(p)).toEqual([]);
  });

  test(`operação sem violações axe — tema ${nome}`, async ({ abrir }) => {
    const p = await comTema(abrir, tema);
    await criarSala(p);
    await p.getByLabel('Marcar ponto para Equipe A').click();
    expect(await analisar(p)).toEqual([]);
  });

  test(`espectador sem violações axe — tema ${nome}`, async ({ abrir }) => {
    const admin = await abrir();
    const sala = await criarSala(admin);
    const p = await comTema(abrir, tema);
    await entrarNaSala(p, sala.id);
    await p.mouse.click(195, 400);
    await expect(p.getByLabel(/Mais ações/)).toBeVisible();
    expect(await analisar(p)).toEqual([]);
  });

  test(`menu e presentes sem violações axe — tema ${nome}`, async ({ abrir }) => {
    const p = await comTema(abrir, tema);
    await criarSala(p);
    await p.getByLabel(/Mais ações/).click();
    await expect(p.locator('dialog[open]')).toHaveCount(1);
    expect(await analisar(p)).toEqual([]);
  });
}

test('aplicação não depende de CDN: nenhuma requisição externa', async ({ abrir }) => {
  const p = await abrir();
  const externas = [];
  p.on('request', (r) => { if (new URL(r.url()).hostname !== '127.0.0.1') externas.push(r.url()); });
  await criarSala(p);
  await p.getByLabel(/Mais ações/).click();
  await p.waitForLoadState('networkidle');
  expect(externas).toEqual([]);
});
