// CV8.DS2.US3 — sorteio da primeira rodada no navegador real.
import AxeBuilder from '@axe-core/playwright';
import { test, expect } from './apoio.js';

const SEGREDO = 'segredo-e2e';
const CABECALHO = { 'x-owner-secret': SEGREDO };

async function sessaoLimpa(p) {
  await p.request.post('/api/rodada/descartar', { headers: CABECALHO });
  await p.request.post('/api/rodada/cancelar', { headers: CABECALHO });
  await p.request.delete('/api/sessao/quadra', { headers: CABECALHO });
  await p.request.post('/api/sessao/encerrar', { headers: CABECALHO });
}

// Cria e marca presentes pela API, na ordem de chegada dada.
async function chegam(p, lista) {
  const r = await p.request.post('/api/sessao', { headers: CABECALHO });
  expect(r.status()).toBe(201);
  const nomes = [];
  for (const [rotulo, genero, nota] of lista) {
    const nome = `${rotulo} ${Math.random().toString(36).slice(2, 7)}`;
    const j = await p.request.post('/api/jogadores', { headers: CABECALHO, data: { nome, genero, nota } });
    expect(j.status()).toBe(201);
    const { id } = await j.json();
    expect((await p.request.put(`/api/sessao/presencas/${id}`, { headers: CABECALHO })).status()).toBe(200);
    nomes.push(nome);
  }
  return nomes;
}

async function abrirTela(p) {
  await p.goto('/');
  await p.getByRole('button', { name: 'Joguinho', exact: true }).click();
  await p.getByLabel('Segredo do dono').fill(SEGREDO);
  await p.getByRole('button', { name: 'Entrar' }).click();
  await p.getByRole('heading', { name: 'Joguinho', level: 1 }).waitFor();
}

const SEIS = [['Ana', 'M', 90], ['Bia', 'M', 80], ['Caio', 'H', 70], ['Davi', 'H', 60], ['Eva', 'M', 50], ['Fabio', 'H', 40]];

test('menos de 4 presentes: sortear desabilitado com o aviso', async ({ abrir }) => {
  const p = await abrir();
  await sessaoLimpa(p);
  await chegam(p, SEIS.slice(0, 3));
  await abrirTela(p);
  await expect(p.getByRole('button', { name: 'Sortear duplas' })).toBeDisabled();
  await expect(p.getByText('Falta 1 presente para sortear.')).toBeVisible();
});

// Notas próximas: há várias combinações igualmente equilibradas para resortear.
const PROXIMAS = [['Ana', 'M', 60], ['Bia', 'M', 61], ['Caio', 'H', 60], ['Davi', 'H', 59], ['Eva', 'M', 62], ['Fabio', 'H', 61]];

test('sortear, resortear, confirmar, presença travada e cancelar', async ({ abrir }) => {
  const p = await abrir();
  await sessaoLimpa(p);
  const nomes = await chegam(p, PROXIMAS);
  await abrirTela(p);

  await p.getByLabel('Pontos da partida').fill('12');
  await p.getByRole('button', { name: 'Sortear duplas' }).click();
  await expect(p.getByRole('heading', { name: /Proposta 1/ })).toContainText('alvo 12');
  await expect(p.getByRole('status').filter({ hasText: 'Primeira partida' })).toContainText('Time 1 × Time 2');
  const fila = p.locator('ol.fila > li');
  await expect(fila).toHaveCount(3);
  await expect(fila.nth(0)).toContainText('em quadra');
  await expect(fila.nth(1)).toContainText('em quadra');

  // 3 duplas, 3 H e 3 M: cada dupla é mista; todos aparecem uma vez
  const texto = await fila.allInnerTexts();
  for (const nome of nomes) expect(texto.join(' ')).toContain(nome);

  // quem chegou em 1º (Ana) joga na primeira partida
  expect(texto.slice(0, 2).join(' ')).toContain(nomes[0]);

  await p.getByRole('button', { name: 'Resortear' }).click();
  await expect(p.getByText(/Combinação 2 de/)).toBeVisible();

  await p.getByRole('button', { name: 'Confirmar e iniciar' }).click();
  await expect(p.getByRole('heading', { name: /Rodada 1/ })).toContainText('alvo 12');
  await expect(p.getByText('Presença travada')).toBeVisible();
  await expect(p.getByRole('button', { name: `Desmarcar ${nomes[0]}` })).toBeDisabled();
  // encerrar não é mais um beco: abre a confirmação que diz o que se perde
  await p.getByRole('button', { name: 'Encerrar joguinho' }).click();
  await expect(p.getByText(/Encerrar o joguinho a cancela\. Perde-se:/)).toBeVisible();
  await p.getByRole('button', { name: 'Voltar', exact: true }).click();
  await p.reload();
  await expect(p.getByRole('heading', { name: /Rodada 1/ })).toBeVisible();

  await p.getByRole('button', { name: 'Cancelar rodada' }).click();
  await p.getByRole('button', { name: 'Sim, cancelar rodada' }).click();
  await expect(p.getByRole('heading', { name: 'Sortear a rodada' })).toBeVisible();
  await expect(p.getByRole('button', { name: `Desmarcar ${nomes[0]}` })).toBeEnabled();
});

test('descartar volta ao sorteio; ímpar mostra o time incompleto', async ({ abrir }) => {
  const p = await abrir();
  await sessaoLimpa(p);
  const nomes = await chegam(p, SEIS.slice(0, 5));
  await abrirTela(p);
  await p.getByRole('button', { name: 'Sortear duplas' }).click();
  const ultimo = p.locator('ol.fila > li').last();
  await expect(ultimo).toContainText('Incompleto');
  await expect(ultimo).toContainText(nomes[4]); // o último a chegar
  await p.getByRole('button', { name: 'Descartar' }).click();
  await expect(p.getByRole('heading', { name: 'Sortear a rodada' })).toBeVisible();
});

test('proposta sem violações axe', async ({ abrir }) => {
  const p = await abrir({ viewport: { width: 390, height: 844 } });
  await sessaoLimpa(p);
  await chegam(p, SEIS);
  await abrirTela(p);
  await p.getByRole('button', { name: 'Sortear duplas' }).click();
  await p.locator('ol.fila > li').first().waitFor();
  await p.evaluate(() => Promise.all(document.getAnimations().filter((a) => a.effect?.getTiming().iterations !== Infinity).map((a) => a.finished.catch(() => {}))));
  const { violations } = await new AxeBuilder({ page: p }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze();
  expect(violations.map((v) => `${v.id}: ${v.nodes.map((n) => n.target.join(' ') + ' ' + (n.any[0]?.message ?? '')).join(' | ')}`)).toEqual([]);
  await sessaoLimpa(p);
});

// CV8.DS6.US15 — formato trio.
test('formato trio: sorteia 2 trios mistos com 6 presentes', async ({ abrir }) => {
  const p = await abrir();
  await sessaoLimpa(p);
  await chegam(p, SEIS);
  await abrirTela(p);

  await p.getByLabel('Trios').check();
  await p.getByRole('button', { name: 'Sortear trios' }).click();
  await expect(p.getByRole('heading', { name: /Proposta 1/ })).toContainText('trios');
  const times = p.locator('ol.fila > li');
  await expect(times).toHaveCount(2);
  for (const i of [0, 1]) {
    // cada trio tem 3 nomes (separados por " + ") e mistura os sexos
    await expect(times.nth(i).locator('.jogadores')).toContainText(/.+ \+ .+ \+ .+/);
  }
  await p.getByRole('button', { name: 'Descartar' }).click();
});

test('formato trio com menos de 6 presentes: sortear desabilitado', async ({ abrir }) => {
  const p = await abrir();
  await sessaoLimpa(p);
  await chegam(p, SEIS.slice(0, 5));
  await abrirTela(p);
  await p.getByLabel('Trios').check();
  await expect(p.getByRole('button', { name: 'Sortear trios' })).toBeDisabled();
  await expect(p.getByText('Falta 1 presente para sortear.')).toBeVisible();
});

// Ajustes do Joguinho: mensagem por formato, slider de pontos, arrastar a ordem e gerenciar jogadores.
test('mínimo acompanha o formato e o slider vai de 6 a 25', async ({ abrir }) => {
  const p = await abrir();
  await sessaoLimpa(p);
  await chegam(p, SEIS.slice(0, 3));
  await abrirTela(p);
  await expect(p.getByText('Falta 1 presente para sortear.')).toBeVisible();
  await p.getByLabel('Trios').check();
  await expect(p.getByText('Faltam 3 presentes para sortear.')).toBeVisible();
  const slider = p.getByRole('slider', { name: 'Pontos da partida' });
  await expect(slider).toHaveAttribute('min', '6');
  await expect(slider).toHaveAttribute('max', '25');
});

test('arrastar a alça muda a ordem de chegada', async ({ abrir }) => {
  const p = await abrir();
  await sessaoLimpa(p);
  const nomes = await chegam(p, SEIS.slice(0, 4));
  await abrirTela(p);
  const itens = p.locator('ol.lista > li');
  await expect(itens.nth(0)).toContainText(nomes[0]);
  const alca = itens.nth(2).getByRole('button', { name: /Arrastar/ });
  const de = await alca.boundingBox();
  const topo = await itens.nth(0).boundingBox();
  await p.mouse.move(de.x + de.width / 2, de.y + de.height / 2);
  await p.mouse.down();
  await p.mouse.move(de.x + de.width / 2, topo.y + 4, { steps: 8 });
  await p.mouse.up();
  await expect(itens.nth(0)).toContainText(nomes[2]);
  await expect(itens.nth(1)).toContainText(nomes[0]);
  await expect(itens.nth(0).locator('.ordem')).toHaveText('1º');
});

test('gerenciar jogadores abre a tela de jogadores', async ({ abrir }) => {
  const p = await abrir();
  await sessaoLimpa(p);
  await chegam(p, SEIS.slice(0, 2));
  await abrirTela(p);
  await p.getByRole('button', { name: 'Gerenciar jogadores' }).click();
  await expect(p).toHaveURL(/\/jogadores$/);
});


// CV8.DS7.US20 — encerrar o joguinho com rodada ativa cancela a rodada de uma vez.
test('encerrar joguinho com rodada em andamento cancela a rodada e encerra', async ({ abrir }) => {
  const p = await abrir();
  await sessaoLimpa(p);
  await chegam(p, SEIS);
  expect((await p.request.post('/api/rodada/sorteio', { headers: CABECALHO, data: { alvo: 10 } })).status()).toBe(201);
  expect((await p.request.post('/api/rodada/confirmar', { headers: CABECALHO })).status()).toBe(200);
  await abrirTela(p);
  await expect(p.getByRole('heading', { name: /Rodada 1/ })).toBeVisible();
  await p.getByRole('button', { name: 'Encerrar joguinho' }).click();
  await expect(p.getByText(/Perde-se: .*a fila \(1 time\)/)).toBeVisible();
  await p.getByRole('button', { name: 'Cancelar rodada e encerrar' }).click();
  await expect(p.getByRole('heading', { name: 'Nenhum joguinho rolando' })).toBeVisible();
  const estado = await (await p.request.get('/api/sessao', { headers: CABECALHO })).json();
  expect(estado.sessao).toBeNull();
});

test('proposta aberta: encerrar descarta a proposta', async ({ abrir }) => {
  const p = await abrir();
  await sessaoLimpa(p);
  await chegam(p, SEIS);
  expect((await p.request.post('/api/rodada/sorteio', { headers: CABECALHO, data: { alvo: 10 } })).status()).toBe(201);
  await abrirTela(p);
  await expect(p.getByRole('heading', { name: /Proposta 1/ })).toBeVisible();
  await p.getByRole('button', { name: 'Encerrar joguinho' }).click();
  await expect(p.getByText(/Perde-se: a proposta 1 \(os times sorteados\)/)).toBeVisible();
  await p.getByRole('button', { name: 'Cancelar rodada e encerrar' }).click();
  await expect(p.getByRole('heading', { name: 'Nenhum joguinho rolando' })).toBeVisible();
});
