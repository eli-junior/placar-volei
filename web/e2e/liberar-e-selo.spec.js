// CV6.DS1.US7/US8 — topo curto, selo de papel e liberar a quadra.
import { test, expect, criarSala, entrarNaSala } from './apoio.js';

test('topo mostra o alvo curto e o selo Ⓐ com dica', async ({ abrir }) => {
  const admin = await abrir({ viewport: { width: 1280, height: 800 } });
  await criarSala(admin);
  await expect(admin.locator('.regras-topo [aria-hidden="true"]')).toHaveText(/^10 pts (com vantagem|\(V\))$/);
  const selo = admin.getByRole('button', { name: 'Administrador da quadra' });
  await expect(selo).toHaveText('A');
  await selo.click();
  await expect(admin.getByRole('status').filter({ hasText: 'Administrador da quadra' })).toBeVisible();
});

test('personalizado desliga o slider e vale o número digitado', async ({ abrir }) => {
  const admin = await abrir({ viewport: { width: 1280, height: 800 } });
  await criarSala(admin);
  await admin.getByTitle('Ajustar pontuação e vantagem').click();
  const dialogo = admin.locator('dialog[open]');
  await expect(dialogo.locator('#alvo-slider')).toHaveValue('10');
  await dialogo.getByLabel('Personalizado').check();
  await expect(dialogo.locator('#alvo-slider')).toBeDisabled();
  await dialogo.locator('#alvo-custom').fill('30');
  await dialogo.getByRole('button', { name: 'Salvar Alterações' }).click();
  await expect(admin.locator('.regras-topo')).toContainText(/30 pts (com vantagem|\(V\))/);
});

test('só o admin vê Liberar quadra; confirmar derruba todos', async ({ abrir }) => {
  const admin = await abrir({ viewport: { width: 1280, height: 800 } });
  const sala = await criarSala(admin);
  const esp = await abrir({ viewport: { width: 1280, height: 800 } });
  await entrarNaSala(esp, sala.id);

  await admin.getByRole('button', { name: 'Duplas e regras da partida' }).click();
  const dialogo = admin.locator('dialog[open]');
  await dialogo.getByRole('button', { name: 'Liberar quadra' }).click();
  await expect(dialogo.getByRole('alert')).toContainText('Não dá para desfazer');
  await dialogo.getByRole('button', { name: 'Liberar agora' }).click();

  await expect(admin.getByText('Quadra liberada.')).toBeVisible();
  await expect(esp.getByText('A quadra foi liberada pelo administrador.')).toBeVisible();
  await expect(admin).toHaveURL(/\/$/);
});
