// Destaque do último ponto e faixa de sequência, no operador e no espectador.
import { test, expect, criarSala, entrarNaSala } from './apoio.js';

test('último ponto em destaque e sequência de bolinhas nas duas telas', async ({ abrir }) => {
  const op = await abrir({ viewport: { width: 390, height: 844 } });
  const { id } = await criarSala(op);
  const esp = await abrir({ viewport: { width: 390, height: 844 } });
  await entrarNaSala(esp, id);

  await op.getByLabel('Marcar ponto para Equipe A').click();
  await expect(op.locator('.sequencia .bolinha')).toHaveCount(1);
  await op.getByLabel('Marcar ponto para Equipe B').click();
  await expect(op.locator('.sequencia .bolinha')).toHaveCount(2);
  await op.getByLabel('Marcar ponto para Equipe B').click();

  for (const p of [op, esp]) {
    const bolinhas = p.locator('.sequencia .bolinha');
    await expect(bolinhas).toHaveCount(3);
    await expect(bolinhas.nth(0)).toHaveClass(/time-a/);
    await expect(bolinhas.nth(2)).toHaveClass(/time-b/);
    await expect(p.locator('.time-b.ultimo')).toHaveCount(1);
    await expect(p.locator('.time-a.apagado')).toHaveCount(1);
  }
  await op.screenshot({ path: 'test-results/sequencia-operador.png' });
  await esp.screenshot({ path: 'test-results/sequencia-espectador.png' });

  await op.locator('.btn-desfazer').click();
  for (const p of [op, esp]) {
    await expect(p.locator('.sequencia .bolinha')).toHaveCount(2);
    await expect(p.locator('.time-b.ultimo')).toHaveCount(1);
  }
  await op.locator('.btn-desfazer').click();
  for (const p of [op, esp]) {
    await expect(p.locator('.sequencia .bolinha')).toHaveCount(1);
    await expect(p.locator('.time-a.ultimo')).toHaveCount(1);
  }
});
