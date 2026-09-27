// CV4.DS3.US2 — superfícies auxiliares e estados coerentes.
import { test, expect, criarSala, entrarNaSala } from './apoio.js';

test('menu por papel e foco de volta ao ⋯', async ({ abrir }) => {
  const admin = await abrir({ viewport: { width: 390, height: 844 } });
  const sala = await criarSala(admin);
  const mais = admin.getByLabel(/Mais ações/);
  await mais.click();
  await expect(admin.locator('.menu-acoes button')).toHaveText(['Compartilhar e QR', 'Duplas e regras', 'Linha do tempo', 'Relógio', 'Modo sol', 'Fechar']);
  await admin.getByRole('button', { name: 'Duplas e regras' }).click();
  await expect(admin.locator('dialog[open]')).toHaveCount(1);
  await admin.keyboard.press('Escape');
  await expect(mais).toBeFocused();

  const esp = await abrir({ viewport: { width: 360, height: 640 } });
  await entrarNaSala(esp, sala.id);
  await esp.mouse.click(180, 320);
  await esp.getByLabel(/Mais ações/).click();
  await expect(esp.locator('.menu-acoes button')).toHaveText(['Compartilhar e QR', 'Girar para paisagem', 'Modo sol', 'Fechar']);
  await expect(esp.locator('dialog[open] .badge')).toHaveCount(2);
  await esp.keyboard.press('Escape');
  await expect(esp.getByLabel(/Mais ações/)).toBeFocused();
});

test('campo do formulário continua visível com o teclado aberto', async ({ abrir }) => {
  const p = await abrir({ viewport: { width: 390, height: 844 } });
  await criarSala(p);
  await p.getByLabel(/Mais ações/).click();
  await p.getByRole('button', { name: 'Duplas e regras' }).click();
  await p.setViewportSize({ width: 390, height: 380 });
  const campo = p.locator('dialog[open] input').first();
  await campo.focus();
  await expect.poll(() => campo.evaluate((e) => { const r = e.getBoundingClientRect(); return r.top >= 0 && r.bottom <= innerHeight; })).toBe(true);
});

test('vitória chega aos dois clientes', async ({ abrir }) => {
  const admin = await abrir({ viewport: { width: 390, height: 844 } });
  const sala = await criarSala(admin, { config: { alvo: 3, vantagem: false } });
  const esp = await abrir({ viewport: { width: 390, height: 844 } });
  await entrarNaSala(esp, sala.id);
  for (let i = 0; i < 3; i++) await admin.getByLabel('Marcar ponto para Equipe A').click();
  await expect(admin.locator('dialog[open]')).toContainText('FIM DE JOGO');
  await expect(esp.getByText(/Equipe A venceu/)).toBeVisible();
});
