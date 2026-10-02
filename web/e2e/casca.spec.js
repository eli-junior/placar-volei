// CV7.TS1 — tela inicial do APK, simulada no navegador com um Capacitor falso.
import AxeBuilder from '@axe-core/playwright';
import { test, expect, comCasca, servidorNoAr, servidorFora, backendFora, abrirCasca } from './apoio.js';

async function analisar(p) {
  await p.evaluate(() => Promise.all(document.getAnimations().map((a) => a.finished.catch(() => {}))));
  const { violations } = await new AxeBuilder({ page: p }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze();
  return violations.map((v) => `${v.id}: ${v.nodes[0]?.target.join(' ')}`);
}

for (const tema of [null, 'sol']) {
  test(`casca: escolha de servidor sem violações axe — tema ${tema ?? 'escuro'}`, async ({ abrir, baseURL }) => {
    const p = await abrir({ viewport: { width: 390, height: 844 } }, { ...comCasca, arg: tema });
    await servidorNoAr(p);
    await abrirCasca(p, baseURL);
    await expect(p.getByRole('heading', { name: 'Quadra online' })).toBeVisible();
    await expect(p.getByText('Servidor disponível.')).toBeVisible();
    expect(await analisar(p)).toEqual([]);
    await p.screenshot({ path: `test-results/casca-${tema ?? 'escuro'}.png` });
  });
}

test('casca: servidor fixo, testa a conexão e só então libera o botão', async ({ abrir, baseURL }) => {
  const p = await abrir({ viewport: { width: 390, height: 844 } }, comCasca);
  await servidorNoAr(p);
  await abrirCasca(p, baseURL);
  await expect(p.getByText(baseURL, { exact: true })).toBeVisible();
  await expect(p.getByLabel('Servidor')).toHaveCount(0);
  const botao = p.getByRole('button', { name: 'Abrir quadras online' });
  await expect(botao).toBeEnabled();
  await botao.click();
  await expect(p).toHaveURL(`${baseURL}/`);
  // No servidor (fora de localhost) volta a home de sempre, mesmo com o Capacitor.
  await expect(p.getByRole('tab', { name: /Acompanhar/ })).toBeVisible();
});

test('casca: sem rede ou com o backend fora, o botão online fica bloqueado e permite testar de novo', async ({ abrir, baseURL }) => {
  for (const fora of [servidorFora, backendFora]) {
    const p = await abrir({ viewport: { width: 390, height: 844 } }, comCasca);
    await fora(p);
    await abrirCasca(p, baseURL);
    await expect(p.getByText('Sem comunicação com o servidor.')).toBeVisible();
    await expect(p.getByRole('button', { name: 'Abrir quadras online' })).toBeDisabled();
    await p.unroute('**/health');
    await servidorNoAr(p);
    await p.getByRole('button', { name: 'Testar de novo' }).click();
    await expect(p.getByRole('button', { name: 'Abrir quadras online' })).toBeEnabled();
  }
});
