// CV8.DS1.US1 — cadastro de jogadores pelo navegador real.
import AxeBuilder from '@axe-core/playwright';
import { test, expect } from './apoio.js';

const SEGREDO = 'segredo-e2e';

async function abrirTela(p) {
  await p.goto('/');
  await p.getByRole('button', { name: 'Jogadores', exact: true }).click();
  await p.getByLabel('Segredo do dono').fill(SEGREDO);
  await p.getByRole('button', { name: 'Entrar' }).click();
  await p.getByRole('heading', { name: 'Novo jogador' }).waitFor();
}

async function cadastrar(p, nome, genero) {
  await p.getByLabel('Nome', { exact: true }).fill(nome);
  await p.getByLabel(genero === 'H' ? 'Homem' : 'Mulher').check();
  await p.getByRole('button', { name: 'Cadastrar' }).click();
}

test('segredo errado é recusado e nada aparece', async ({ abrir }) => {
  const p = await abrir();
  await p.goto('/');
  await p.getByRole('button', { name: 'Jogadores', exact: true }).click();
  await p.getByLabel('Segredo do dono').fill('errado');
  await p.getByRole('button', { name: 'Entrar' }).click();
  await expect(p.getByRole('alert')).toContainText('Segredo recusado');
  await expect(p.getByRole('heading', { name: 'Novo jogador' })).toHaveCount(0);
});

test('cadastrar, repetir nome, editar, inativar e reativar', async ({ abrir }) => {
  const nome = `Ana ${Math.random().toString(36).slice(2, 7)}`;
  const p = await abrir();
  await abrirTela(p);

  await cadastrar(p, nome, 'M');
  await expect(p.getByRole('listitem').filter({ hasText: nome })).toBeVisible();

  await cadastrar(p, nome.toUpperCase(), 'M');
  await expect(p.getByRole('alert')).toContainText('já está em uso');

  await p.getByRole('button', { name: `Editar ${nome}` }).click();
  await p.getByLabel('Homem').check();
  await p.getByRole('button', { name: 'Salvar' }).click();
  await expect(p.getByRole('listitem').filter({ hasText: nome })).toContainText('Homem');

  await p.getByRole('button', { name: `Inativar ${nome}` }).click();
  await expect(p.getByRole('button', { name: `Reativar ${nome}` })).toBeVisible();
  await p.getByRole('button', { name: `Reativar ${nome}` }).click();
  await expect(p.getByRole('button', { name: `Inativar ${nome}` })).toBeVisible();
});

test('formulário vazio aponta o campo e o segredo fica lembrado', async ({ abrir }) => {
  const p = await abrir();
  await abrirTela(p);
  await p.getByRole('button', { name: 'Cadastrar' }).click();
  await expect(p.getByRole('alert')).toContainText('Nome é obrigatório');
  await p.reload();
  await expect(p.getByRole('heading', { name: 'Novo jogador' })).toBeVisible();
});

const PNG = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==', 'base64');

test('nota padrão 60, nome com 2 palavras e nota inválida', async ({ abrir }) => {
  const nome = `Caio ${Math.random().toString(36).slice(2, 7)}`;
  const p = await abrir();
  await abrirTela(p);
  await cadastrar(p, 'Caio', 'H');
  await expect(p.getByRole('alert')).toContainText('nome e sobrenome');
  await p.getByLabel('Nome', { exact: true }).fill(nome);
  await p.getByLabel('Nota').fill('101');
  await p.getByRole('button', { name: 'Cadastrar' }).click();
  await expect(p.getByRole('alert')).toContainText('1 a 100');
  await p.getByLabel('Nota').fill('');
  await p.getByRole('button', { name: 'Cadastrar' }).click();
  await expect(p.getByRole('listitem').filter({ hasText: nome })).toContainText('nota 60');
  await p.getByRole('button', { name: `Editar ${nome}` }).click();
  await p.getByLabel('Nota').fill('85');
  await p.getByRole('button', { name: 'Salvar' }).click();
  await expect(p.getByRole('listitem').filter({ hasText: nome })).toContainText('nota 85');
});

test('foto: envia, aparece na lista, persiste ao recarregar e remove', async ({ abrir }) => {
  const nome = `Dani ${Math.random().toString(36).slice(2, 7)}`;
  const p = await abrir();
  await abrirTela(p);
  await p.getByLabel('Nome', { exact: true }).fill(nome);
  await p.getByLabel('Mulher').check();
  await p.locator('input[type=file]').setInputFiles({ name: 'foto.png', mimeType: 'image/png', buffer: PNG });
  await expect(p.getByAltText('Foto do jogador')).toBeVisible();
  await p.getByRole('button', { name: 'Cadastrar' }).click();
  const item = p.getByRole('listitem').filter({ hasText: nome });
  await expect(item.locator('img.avatar')).toBeVisible();
  await p.reload();
  await expect(p.getByRole('listitem').filter({ hasText: nome }).locator('img.avatar')).toBeVisible();

  await p.getByRole('button', { name: `Editar ${nome}` }).click();
  await p.getByRole('button', { name: 'Remover foto' }).click();
  await p.getByRole('button', { name: 'Salvar' }).click();
  await expect(p.getByRole('listitem').filter({ hasText: nome }).locator('img.avatar')).toHaveCount(0);
});

test('tela de jogadores sem violações axe', async ({ abrir }) => {
  const p = await abrir({ viewport: { width: 390, height: 844 } });
  await abrirTela(p);
  await cadastrar(p, `Bia ${Math.random().toString(36).slice(2, 7)}`, 'M');
  await p.getByRole('listitem').first().waitFor();
  await p.evaluate(() => Promise.all(document.getAnimations().filter((a) => a.effect?.getTiming().iterations !== Infinity).map((a) => a.finished.catch(() => {}))));
  const { violations } = await new AxeBuilder({ page: p }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze();
  expect(violations.map((v) => `${v.id}: ${v.nodes.map((n) => n.target.join(' ') + ' ' + (n.any[0]?.message ?? '')).join(' | ')}`)).toEqual([]);
});

test('dentro do APK a entrada de jogadores não aparece', async ({ abrir }) => {
  const p = await abrir({}, { fn: () => { window.Capacitor = { isNativePlatform: () => true }; } });
  await p.goto('/');
  await p.getByRole('tab', { name: 'Criar placar' }).waitFor();
  await expect(p.getByRole('button', { name: 'Jogadores', exact: true })).toHaveCount(0);
});

// CV8.DS7.US17 — o segredo salvo só some quando o servidor o recusa.
const guardado = (p) => p.evaluate(() => localStorage.getItem('placar:segredo_dono'));

test('404 de domínio não apaga o segredo salvo', async ({ abrir }) => {
  const nome = `Eva ${Math.random().toString(36).slice(2, 7)}`;
  const p = await abrir();
  await abrirTela(p);
  await cadastrar(p, nome, 'M');
  await expect(p.getByRole('listitem').filter({ hasText: nome })).toBeVisible();

  await p.route('**/api/jogadores/*', (rota) =>
    rota.request().method() === 'PATCH'
      ? rota.fulfill({ status: 404, contentType: 'application/json', body: JSON.stringify({ detail: 'Jogador não encontrado.', erros: [{ campo: 'jogador', tipo: 'not_found' }] }) })
      : rota.continue());
  await p.getByRole('button', { name: `Editar ${nome}` }).click();
  await p.getByLabel('Homem').check();
  await p.getByRole('button', { name: 'Salvar' }).click();
  await expect(p.getByRole('alert')).toContainText('não encontrado');
  expect(await guardado(p)).toBe(SEGREDO);
  await expect(p.getByRole('button', { name: 'Esquecer segredo neste aparelho' })).toBeVisible();
});

test('429 não apaga o segredo e diz quanto falta', async ({ abrir }) => {
  const p = await abrir();
  await abrirTela(p);
  await p.route('**/api/jogadores?*', (rota) =>
    rota.fulfill({ status: 429, headers: { 'retry-after': '240' }, contentType: 'application/json', body: JSON.stringify({ detail: 'Muitas tentativas incorretas.' }) }));
  await p.reload();
  await expect(p.getByRole('alert')).toContainText('Tente de novo em 4 min');
  expect(await guardado(p)).toBe(SEGREDO);
  await p.unroute('**/api/jogadores?*');
  await p.reload();
  await expect(p.getByRole('heading', { name: 'Novo jogador' })).toBeVisible();
});

test('segredo errado salvo é esquecido', async ({ abrir }) => {
  const p = await abrir();
  await p.goto('/');
  await p.evaluate(() => localStorage.setItem('placar:segredo_dono', 'errado'));
  await p.getByRole('button', { name: 'Jogadores', exact: true }).click();
  await expect(p.getByRole('alert')).toContainText('Segredo recusado');
  expect(await guardado(p)).toBeNull();
});

test('joguinho: bloqueio no WebSocket (4429) não apaga o segredo', async ({ abrir }) => {
  const p = await abrir();
  await p.routeWebSocket('**/ws/gerenciador', (ws) => ws.close({ code: 4429, reason: 'bloqueado' }));
  await p.goto('/');
  await p.evaluate((s) => localStorage.setItem('placar:segredo_dono', s), SEGREDO);
  await p.getByRole('button', { name: 'Joguinho', exact: true }).click();
  await expect(p.getByRole('alert')).toContainText('Muitas tentativas incorretas');
  expect(await guardado(p)).toBe(SEGREDO);
});
