// CV7.TS1 — tela inicial do APK, simulada no navegador com um Capacitor falso.
import AxeBuilder from '@axe-core/playwright';
import { test, expect } from './apoio.js';

const comCasca = { fn: (tema) => {
  window.Capacitor = { isNativePlatform: () => true };
  try { if (tema) localStorage.setItem('placar:tema', tema); } catch {}
}, arg: null };

async function analisar(p) {
  await p.evaluate(() => Promise.all(document.getAnimations().map((a) => a.finished.catch(() => {}))));
  const { violations } = await new AxeBuilder({ page: p }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze();
  return violations.map((v) => `${v.id}: ${v.nodes[0]?.target.join(' ')}`);
}

for (const tema of [null, 'sol']) {
  test(`casca: escolha de servidor sem violações axe — tema ${tema ?? 'escuro'}`, async ({ abrir, baseURL }) => {
    const p = await abrir({ viewport: { width: 390, height: 844 } }, { ...comCasca, arg: tema });
    await p.goto(baseURL.replace('127.0.0.1', 'localhost'));
    await expect(p.getByRole('heading', { name: 'Quadra online' })).toBeVisible();
    expect(await analisar(p)).toEqual([]);
    await p.screenshot({ path: `test-results/casca-${tema ?? 'escuro'}.png` });
  });
}

test('casca: servidor fixo, testa a conexão e só então libera o botão', async ({ abrir, baseURL }) => {
  const p = await abrir({ viewport: { width: 390, height: 844 } }, comCasca);
  await p.goto(baseURL.replace('127.0.0.1', 'localhost'));
  await expect(p.getByText(baseURL, { exact: true })).toBeVisible();
  await expect(p.getByLabel('Servidor')).toHaveCount(0);
  const botao = p.getByRole('button', { name: 'Abrir quadras online' });
  await expect(botao).toBeEnabled();
  await botao.click();
  await expect(p).toHaveURL(`${baseURL}/`);
  // No servidor (fora de localhost) volta a home de sempre, mesmo com o Capacitor.
  await expect(p.getByRole('tab', { name: /Acompanhar/ })).toBeVisible();
});

test('casca: servidor fora do ar mantém o botão bloqueado e permite testar de novo', async ({ abrir, baseURL }) => {
  const p = await abrir({ viewport: { width: 390, height: 844 } }, comCasca);
  await p.route('**/health', (rota) => rota.abort());
  await p.goto(baseURL.replace('127.0.0.1', 'localhost'));
  await expect(p.getByText(/Servidor indisponível/)).toBeVisible();
  await expect(p.getByRole('button', { name: 'Abrir quadras online' })).toBeDisabled();
  await p.unroute('**/health');
  await p.getByRole('button', { name: 'Testar de novo' }).click();
  await expect(p.getByRole('button', { name: 'Abrir quadras online' })).toBeEnabled();
});
