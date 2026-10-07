// CV8.DS1.US1 — cadastro de jogadores pelo navegador real.
import AxeBuilder from '@axe-core/playwright';
import { test, expect } from './apoio.js';

const SEGREDO = 'segredo-e2e';

async function abrirTela(p) {
  await p.goto('/');
  await p.getByRole('button', { name: 'Jogadores' }).click();
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
  await p.getByRole('button', { name: 'Jogadores' }).click();
  await p.getByLabel('Segredo do dono').fill('errado');
  await p.getByRole('button', { name: 'Entrar' }).click();
  await expect(p.getByRole('alert')).toContainText('Segredo recusado');
  await expect(p.getByRole('heading', { name: 'Novo jogador' })).toHaveCount(0);
});

test('cadastrar, repetir nome, editar, inativar e reativar', async ({ abrir }) => {
  const nome = `Ana${Math.random().toString(36).slice(2, 7)}`;
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

test('tela de jogadores sem violações axe', async ({ abrir }) => {
  const p = await abrir({ viewport: { width: 390, height: 844 } });
  await abrirTela(p);
  await cadastrar(p, `Bia${Math.random().toString(36).slice(2, 7)}`, 'M');
  await p.getByRole('listitem').first().waitFor();
  const { violations } = await new AxeBuilder({ page: p }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze();
  expect(violations.map((v) => v.id)).toEqual([]);
});

test('dentro do APK a entrada de jogadores não aparece', async ({ abrir }) => {
  const p = await abrir({}, { fn: () => { window.Capacitor = { isNativePlatform: () => true }; } });
  await p.goto('/');
  await p.getByRole('tab', { name: 'Criar placar' }).waitFor();
  await expect(p.getByRole('button', { name: 'Jogadores' })).toHaveCount(0);
});
