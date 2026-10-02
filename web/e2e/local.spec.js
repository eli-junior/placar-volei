// CV7.US1 — quadra local do APK: só sem comunicação com o servidor.
import AxeBuilder from '@axe-core/playwright';
import { test, expect, comCasca, servidorNoAr, servidorFora, backendFora, abrirCasca } from './apoio.js';

const VIEWPORT = { viewport: { width: 390, height: 844 } };
const criar = (p) => p.getByRole('button', { name: 'Criar quadra local' });
const continuar = (p) => p.getByRole('button', { name: 'Continuar quadra local' });
const online = (p) => p.getByRole('button', { name: 'Abrir quadras online' });
const placar = (p) => p.locator('[aria-label^="Placar:"]');

async function analisar(p) {
  await p.evaluate(() => Promise.all(document.getAnimations().filter((a) => a.effect?.getTiming().iterations !== Infinity).map((a) => a.finished.catch(() => {}))));
  const { violations } = await new AxeBuilder({ page: p }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze();
  return violations.map((v) => `${v.id}: ${v.nodes[0]?.target.join(' ')}`);
}

/** Abre o app sem comunicação com o servidor e entra na quadra local. */
async function entrarNaLocal(p, baseURL, fora = servidorFora) {
  await fora(p);
  await abrirCasca(p, baseURL);
  await expect(criar(p).or(continuar(p))).toBeEnabled();
  await criar(p).or(continuar(p)).click();
  await expect(p.getByLabel('Marcar ponto para Equipe A')).toBeVisible();
}

test('com o servidor no ar a quadra local nem habilita', async ({ abrir, baseURL }) => {
  const p = await abrir(VIEWPORT, comCasca);
  await servidorNoAr(p);
  await abrirCasca(p, baseURL);
  await expect(online(p)).toBeEnabled();
  await expect(criar(p)).toBeDisabled();
  await expect(p.getByText('só é usada quando não há conexão')).toBeVisible();
});

test('enquanto testa a conexão, nenhum dos dois modos está liberado', async ({ abrir, baseURL }) => {
  const p = await abrir(VIEWPORT, comCasca);
  await p.route('**/health', () => {});
  await abrirCasca(p, baseURL);
  await expect(p.getByText('Testando a conexão…')).toBeVisible();
  await expect(online(p)).toBeDisabled();
  await expect(criar(p)).toBeDisabled();
});

for (const [rotulo, fora] of [['sem rede', servidorFora], ['túnel no ar e backend fora (502)', backendFora]]) {
  test(`${rotulo}: só a quadra local libera, e ela funciona até o fim e depois de reabrir`, async ({ abrir, baseURL }) => {
    const p = await abrir(VIEWPORT, comCasca);
    const chamadas = [];
    await fora(p);
    await abrirCasca(p, baseURL);
    await expect(online(p)).toBeDisabled();
    await expect(criar(p)).toBeEnabled();
    p.on('request', (r) => chamadas.push(r.url()));
    await criar(p).click();

    const a = p.getByLabel('Marcar ponto para Equipe A');
    const b = p.getByLabel('Marcar ponto para Equipe B');
    await expect(p.getByRole('img', { name: 'Quadra local, sem internet' })).toBeVisible();
    await a.click();
    await a.click();
    await b.click();
    await p.locator('.btn-desfazer').click();
    await expect(placar(p)).toHaveAttribute('aria-label', 'Placar: Equipe A 2, Equipe B 0');
    // Nada de servidor, relógio, compartilhar nem presentes na quadra local.
    await expect(p.getByLabel('Relógio')).toHaveCount(0);
    await expect(p.getByRole('button', { name: /Compartilhar/ })).toHaveCount(0);

    // Fechar e abrir o app: a quadra continua, e a tela inicial oferece Continuar.
    await abrirCasca(p, baseURL);
    await expect(criar(p)).toHaveCount(0);
    await continuar(p).click();
    await expect(placar(p)).toHaveAttribute('aria-label', 'Placar: Equipe A 2, Equipe B 0');

    // Até o fim da partida e a próxima.
    for (let i = 0; i < 8; i++) await a.click();
    await expect(p.getByRole('heading', { name: /Venceu!/ })).toBeVisible();
    await p.getByRole('button', { name: 'Reinício Rápido' }).click();
    await expect(placar(p)).toHaveAttribute('aria-label', 'Placar: Equipe A 0, Equipe B 0');
    // A nova partida herda as regras e a quadra segue em andamento.
    await expect(p.locator('.regras-topo')).toContainText(/10 pts/);
    await a.click();
    await expect(placar(p)).toHaveAttribute('aria-label', 'Placar: Equipe A 1, Equipe B 0');

    expect(chamadas.filter((u) => /\/api\/|\/ws\//.test(u))).toEqual([]);
  });
}

test('partida local em andamento continua liberada com o servidor de volta; encerrada, não', async ({ abrir, baseURL }) => {
  const p = await abrir(VIEWPORT, comCasca);
  await entrarNaLocal(p, baseURL);
  await p.getByLabel('Marcar ponto para Equipe A').click();

  await p.unroute('**/health');
  await servidorNoAr(p);
  await abrirCasca(p, baseURL);
  await expect(online(p)).toBeEnabled();
  await expect(continuar(p)).toBeEnabled();
  await expect(p.getByText('Há uma partida em andamento nesta quadra.')).toBeVisible();
  await continuar(p).click();
  const a = p.getByLabel('Marcar ponto para Equipe A');
  for (let i = 0; i < 9; i++) await a.click();
  await expect(p.getByRole('heading', { name: /Venceu!/ })).toBeVisible();

  await abrirCasca(p, baseURL);
  await expect(online(p)).toBeEnabled();
  await expect(continuar(p)).toBeDisabled();
});

test('duplas, regras e tema se ajustam na quadra local e ficam guardados', async ({ abrir, baseURL }) => {
  const p = await abrir({ viewport: { width: 1280, height: 800 } }, comCasca);
  await entrarNaLocal(p, baseURL);
  await p.getByTitle('Ajustar pontuação e vantagem').click();
  const dialogo = p.locator('dialog[open]');
  await dialogo.getByLabel('Personalizado').check();
  await dialogo.locator('#alvo-custom').fill('15');
  await dialogo.getByRole('button', { name: 'Salvar Alterações' }).click();
  await expect(p.locator('.regras-topo')).toContainText(/15 pts/);

  await abrirCasca(p, baseURL);
  await continuar(p).click();
  await expect(p.locator('.regras-topo')).toContainText(/15 pts/);
});

test('voltar da sala atualiza a tela inicial sem recarregar o app', async ({ abrir, baseURL }) => {
  const p = await abrir(VIEWPORT, comCasca);
  await entrarNaLocal(p, baseURL);
  await p.unroute('**/health');
  await servidorNoAr(p);
  // Sai e volta pela própria interface: o teste de conexão roda de novo ao montar.
  await p.getByLabel('Voltar ao início').click();
  await expect(p.getByText('Servidor disponível.')).toBeVisible();
  await expect(continuar(p)).toBeEnabled();
  await continuar(p).click();
  const a = p.getByLabel('Marcar ponto para Equipe A');
  for (let i = 0; i < 10; i++) await a.click();
  await expect(p.getByRole('heading', { name: /Venceu!/ })).toBeVisible();
  await p.getByRole('button', { name: 'Ver Placar e Linha do Tempo' }).click();
  await p.getByLabel('Voltar ao início').click();
  await expect(p.getByText('Servidor disponível.')).toBeVisible();
  await expect(continuar(p)).toBeDisabled();
  await expect(online(p)).toBeEnabled();
});

test('apagar a quadra local pede confirmação e volta ao início', async ({ abrir, baseURL }) => {
  const p = await abrir(VIEWPORT, comCasca);
  await entrarNaLocal(p, baseURL);
  await p.getByRole('button', { name: 'Duplas e regras da partida' }).click();
  const dialogo = p.locator('dialog[open]');
  await dialogo.getByRole('button', { name: 'Apagar quadra local' }).click();
  await expect(dialogo.getByRole('alert')).toContainText('Não dá para desfazer');
  await dialogo.getByRole('button', { name: 'Apagar agora' }).click();
  await expect(criar(p)).toBeEnabled();
  await abrirCasca(p, baseURL);
  await expect(criar(p)).toBeEnabled();
});

test('dados ilegíveis avisam e deixam começar do zero', async ({ abrir, baseURL }) => {
  const p = await abrir(VIEWPORT, { fn: () => {
    window.Capacitor = { isNativePlatform: () => true };
    localStorage.setItem('placar.quadra_local', '{"versao":1,"eventos":[1]}');
  }, arg: null });
  await servidorFora(p);
  await abrirCasca(p, baseURL);
  await expect(p.getByRole('alert')).toContainText('ilegíveis');
  await p.getByRole('button', { name: 'Começar do zero' }).click();
  await expect(p.getByRole('alert')).toHaveCount(0);
  await expect(criar(p)).toBeEnabled();
});

for (const tema of [null, 'sol']) {
  test(`quadra local sem violações axe — tema ${tema ?? 'escuro'}`, async ({ abrir, baseURL }) => {
    const p = await abrir(VIEWPORT, { ...comCasca, arg: tema });
    await entrarNaLocal(p, baseURL);
    await p.getByLabel('Marcar ponto para Equipe A').click();
    expect(await analisar(p)).toEqual([]);
  });
}
