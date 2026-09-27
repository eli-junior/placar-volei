// CV4.DS2.US2 — imersão estável e tela cheia real.
import { test, expect, criarSala, entrarNaSala } from './apoio.js';

for (const [largura, altura] of [[360, 640], [390, 844], [1066, 600]]) {
  test(`placar do espectador não se move ao revelar controles (${largura}×${altura})`, async ({ abrir }) => {
    const admin = await abrir();
    const sala = await criarSala(admin);
    const esp = await abrir({ viewport: { width: largura, height: altura }, hasTouch: true });
    await entrarNaSala(esp, sala.id);
    await expect(esp.getByLabel('Tela cheia')).toHaveCount(0, { timeout: 6000 });
    const antes = await esp.locator('.area-resultado').boundingBox();
    await esp.touchscreen.tap(largura / 2, altura / 2);
    await expect(esp.getByLabel('Tela cheia')).toBeVisible();
    expect(await esp.locator('.area-resultado').boundingBox()).toEqual(antes);
    const fora = await esp.evaluate(() => [...document.querySelectorAll('.barra-sala button, .status-topo')]
      .filter((e) => e.getBoundingClientRect().right > innerWidth + 1).length);
    expect(fora).toBe(0);
  });
}

test('toque que revela os controles não aciona o botão oculto', async ({ abrir }) => {
  const admin = await abrir();
  const sala = await criarSala(admin);
  const esp = await abrir({ viewport: { width: 390, height: 844 }, hasTouch: true });
  await entrarNaSala(esp, sala.id);
  await esp.touchscreen.tap(195, 400);
  const botao = esp.getByLabel('Tela cheia');
  const caixa = await botao.boundingBox();
  await expect(botao).toHaveCount(0, { timeout: 6000 });
  // Toca exatamente onde o botão aparecerá: só revela, não entra em tela cheia.
  await esp.touchscreen.tap(caixa.x + caixa.width / 2, caixa.y + caixa.height / 2);
  await expect(esp.getByLabel('Tela cheia')).toBeVisible();
  expect(await esp.evaluate(() => Boolean(document.fullscreenElement))).toBe(false);
});

test('tela cheia confirmada pelo navegador e saída externa reconhecida', async ({ abrir }) => {
  const admin = await abrir();
  const sala = await criarSala(admin);
  const esp = await abrir({ viewport: { width: 390, height: 844 } });
  await entrarNaSala(esp, sala.id);
  await esp.mouse.click(195, 400);
  await esp.getByLabel('Tela cheia').click();
  await expect(esp.getByLabel('Sair da tela cheia')).toBeVisible();
  await esp.evaluate(() => document.exitFullscreen());
  await expect(esp.getByLabel('Tela cheia')).toBeVisible();
});

test('recusa de tela cheia informa e mantém o placar na aba', async ({ abrir }) => {
  const admin = await abrir();
  const sala = await criarSala(admin);
  const esp = await abrir({ viewport: { width: 390, height: 844 } }, {
    fn: () => { Element.prototype.requestFullscreen = () => Promise.reject(new TypeError('negado')); },
  });
  await entrarNaSala(esp, sala.id);
  await esp.mouse.click(195, 400);
  await esp.getByLabel('Tela cheia').click();
  await expect(esp.getByText('O navegador não permitiu a tela cheia. O placar continua nesta aba.')).toBeVisible();
  await expect(esp.getByLabel('Tela cheia')).toBeVisible();
});

// CV6.DS1.US3: empilhado em tela em pé e três dígitos cabem no maior tamanho.
test('números empilhados cabem com 100 pontos no tamanho G', async ({ abrir }) => {
  test.setTimeout(90_000);
  const p = await abrir({ viewport: { width: 344, height: 882 } }, { fn: () => localStorage.setItem('placar:tamanho_numeros', 'G') });
  await criarSala(p, { config: { alvo: 100, vantagem: false } });
  const a = p.getByLabel('Marcar ponto para Equipe A');
  for (let i = 0; i < 100; i++) await a.click();
  await p.keyboard.press('Escape');
  const caixas = await p.evaluate(() => [...document.querySelectorAll('.resultado .time')].map((t) => {
    const n = t.querySelector('strong').getBoundingClientRect();
    const c = t.getBoundingClientRect();
    return { dentro: n.left >= c.left - 1 && n.right <= c.right + 1, topo: c.top };
  }));
  expect(caixas.every((c) => c.dentro)).toBe(true);
  expect(caixas[1].topo).toBeGreaterThan(caixas[0].topo);
});

// Escala P/M/G também no placar clássico: cresce de P para G e cabe no cartão.
for (const [nome, viewport] of [['tablet', { width: 1280, height: 800 }], ['fold fechado', { width: 344, height: 882 }]]) {
  test(`clássico segue P/M/G e cabe no cartão (${nome})`, async ({ abrir }) => {
    test.setTimeout(120_000);
    const medidas = {};
    for (const t of ['P', 'M', 'G']) {
      const p = await abrir({ viewport }, { fn: (v) => localStorage.setItem('placar:tamanho_numeros', v), arg: t });
      await criarSala(p, { config: { alvo: 100, vantagem: false, tema_placar: 'classico' } });
      const a = p.getByLabel('Marcar ponto para Equipe A');
      for (let i = 0; i < 100; i++) await a.click();
      await p.getByText('Iniciar Próxima Partida').last().waitFor();
      await p.keyboard.press('Escape');
      await p.waitForTimeout(600);
      if (process.env.CAPTURAS) await p.screenshot({ path: `${process.env.CAPTURAS}/classico-${nome.replace(' ', '-')}-${t}.png` });
      medidas[t] = await p.evaluate(() => [...document.querySelectorAll('.classico .time')].map((s) => {
        const n = s.querySelector('.numero-texto').getBoundingClientRect();
        const c = s.querySelector('.cartao-placa').getBoundingClientRect();
        return { fonte: parseFloat(getComputedStyle(s.querySelector('.numero-texto')).fontSize), dentro: n.left >= c.left - 1 && n.right <= c.right + 1 && n.top >= c.top - 1 && n.bottom <= c.bottom + 1 };
      }));
    }
    for (const t of ['P', 'M', 'G']) expect(medidas[t].every((m) => m.dentro), `tamanho ${t}`).toBe(true);
    expect(medidas.G[1].fonte).toBeGreaterThan(medidas.P[1].fonte);
    expect(medidas.G[0].fonte).toBeGreaterThan(medidas.P[0].fonte);
  });
}
