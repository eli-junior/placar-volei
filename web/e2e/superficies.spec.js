// CV4.DS3.US2 — superfícies auxiliares e estados coerentes.
import { test, expect, criarSala, entrarNaSala } from './apoio.js';

test('menu por papel e foco de volta ao ⋯', async ({ abrir }) => {
  const admin = await abrir({ viewport: { width: 390, height: 844 } });
  const sala = await criarSala(admin);
  const mais = admin.getByLabel(/Mais ações/);
  await mais.click();
  await expect(admin.locator('.menu-acoes button')).toHaveText(['Inverter lados', 'Modo sol', 'Relógio', 'Linha do tempo', 'Números: M', 'Reiniciar partida', 'Fechar']);
  await admin.keyboard.press('Escape');
  await expect(mais).toBeFocused();
  // Duplas e regras mora no cabeçalho (CV6.DS1.US1).
  const ajustes = admin.getByLabel('Duplas e regras da partida');
  await ajustes.click();
  await expect(admin.locator('dialog[open]')).toHaveCount(1);
  await admin.keyboard.press('Escape');
  await expect(ajustes).toBeFocused();

  const esp = await abrir({ viewport: { width: 360, height: 640 } });
  await entrarNaSala(esp, sala.id);
  await esp.mouse.click(180, 320);
  await esp.getByLabel(/Mais ações/).click();
  await expect(esp.locator('.menu-acoes button')).toHaveText(['Inverter lados', 'Modo sol', 'Números: M', 'Girar para paisagem', 'Fechar']);
  await expect(esp.locator('dialog[open] .badge')).toHaveCount(2);
  await esp.keyboard.press('Escape');
  await expect(esp.getByLabel(/Mais ações/)).toBeFocused();
});

test('tela larga: ações sobem para o topo e o ⋯ fica com o resto', async ({ abrir }) => {
  const admin = await abrir({ viewport: { width: 1280, height: 800 } });
  await criarSala(admin, { nome: '' });
  const topo = admin.locator('.barra-sala');
  for (const rotulo of ['Duplas e regras da partida', 'Inverter lados das equipes', 'Modo sol', 'Relógio', 'Linha do tempo', 'Números: M']) {
    await expect(topo.getByLabel(rotulo, { exact: true })).toBeVisible();
  }
  await admin.getByLabel(/Mais ações/).click();
  await expect(admin.locator('.menu-acoes button')).toHaveText(['Fechar']);
  // Nome padrão não repete o código.
  await expect(admin.locator('.chip-codigo span')).toHaveCount(0);
});

test('campo do formulário continua visível com o teclado aberto', async ({ abrir }) => {
  const p = await abrir({ viewport: { width: 390, height: 844 } });
  await criarSala(p);
  await p.getByLabel('Duplas e regras da partida').click();
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

// CV6.DS1.US5: pontuação primeiro e ações sempre alcançáveis, mesmo em tela baixa.
test('configurações: pontuação primeiro e salvar sempre visível', async ({ abrir }) => {
  const p = await abrir({ viewport: { width: 344, height: 882 } });
  await criarSala(p);
  const botaoAjustes = p.getByLabel('Duplas e regras da partida');
  if (await botaoAjustes.isVisible()) {
    await botaoAjustes.click();
  } else {
    await p.getByLabel(/Mais ações/).click();
    await p.getByRole('button', { name: 'Duplas e regras' }).click();
  }
  await expect(p.locator('dialog[open] .secao-rotulo').first()).toHaveText(/Pontuação/i);
  await p.setViewportSize({ width: 344, height: 420 });
  const salvar = p.getByRole('button', { name: 'Salvar Alterações' });
  await expect(salvar).toBeInViewport();
  await p.getByLabel('Jogador 1').first().fill('Ana');
  await expect(salvar).toBeInViewport();
  await salvar.click();
  await expect(p.locator('dialog[open]')).toHaveCount(0);
});
