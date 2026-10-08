// CV8.DS3.US5 — painel da condução, chamar partida no placar e sincronia.
import AxeBuilder from '@axe-core/playwright';
import { test, expect, entrarNaSala } from './apoio.js';

const SEGREDO = 'segredo-e2e';
const CABECALHO = { 'x-owner-secret': SEGREDO };

async function sessaoLimpa(p) {
  await p.request.post('/api/rodada/descartar', { headers: CABECALHO });
  await p.request.post('/api/rodada/cancelar', { headers: CABECALHO });
  await p.request.delete('/api/sessao/quadra', { headers: CABECALHO });
  await p.request.post('/api/sessao/encerrar', { headers: CABECALHO });
}

async function chegam(p, lista) {
  expect((await p.request.post('/api/sessao', { headers: CABECALHO })).status()).toBe(201);
  const nomes = [];
  for (const [rotulo, genero, nota] of lista) {
    const nome = `${rotulo} ${Math.random().toString(36).slice(2, 7)}`;
    const j = await p.request.post('/api/jogadores', { headers: CABECALHO, data: { nome, genero, nota } });
    const { id } = await j.json();
    expect((await p.request.put(`/api/sessao/presencas/${id}`, { headers: CABECALHO })).status()).toBe(200);
    nomes.push(nome);
  }
  return nomes;
}

async function rodadaConfirmada(p, alvo = 12) {
  expect((await p.request.post('/api/rodada/sorteio', { headers: CABECALHO, data: { alvo } })).status()).toBe(201);
  expect((await p.request.post('/api/rodada/confirmar', { headers: CABECALHO })).status()).toBe(200);
}

async function abrirTela(p) {
  await p.goto('/');
  await p.getByRole('button', { name: 'Joguinho', exact: true }).click();
  await p.getByLabel('Segredo do dono').fill(SEGREDO);
  await p.getByRole('button', { name: 'Entrar' }).click();
  await p.getByRole('heading', { name: 'Joguinho', level: 1 }).waitFor();
}

const SEIS = [['Ana', 'M', 90], ['Bia', 'M', 80], ['Caio', 'H', 70], ['Davi', 'H', 60], ['Eva', 'M', 50], ['Fabio', 'H', 40]];

test('sem quadra vinculada a chamada fica bloqueada com o motivo', async ({ abrir }) => {
  const p = await abrir();
  await sessaoLimpa(p);
  await chegam(p, SEIS);
  await rodadaConfirmada(p);
  await abrirTela(p);
  await expect(p.getByRole('heading', { name: /Rodada 1/ })).toContainText('alvo 12');
  await expect(p.getByRole('button', { name: 'Chamar partida' })).toBeDisabled();
  await expect(p.getByText('Vincule uma quadra do placar para chamar a partida.')).toBeVisible();
  // painel inicial: fila, reis e eliminados com os textos vazios
  await expect(p.getByRole('heading', { name: 'Fila (1)' })).toBeVisible();
  await expect(p.getByText('Ninguém com 2 vitórias seguidas ainda.')).toBeVisible();
  await expect(p.getByText('Ninguém perdeu ainda.')).toBeVisible();
  await expect(p.getByRole('status').filter({ hasText: 'Time 1 × Time 2' })).toBeVisible();
});

test('criar quadra, vincular, chamar partida e ver as duplas no placar', async ({ abrir }) => {
  const p = await abrir();
  await sessaoLimpa(p);
  const nomes = await chegam(p, SEIS);
  await rodadaConfirmada(p, 12);
  await abrirTela(p);

  await p.getByRole('button', { name: 'Criar quadra e vincular' }).click();
  await expect(p.getByText('disponível', { exact: true })).toBeVisible();
  const link = p.getByRole('link', { name: 'Abrir o placar' });
  const href = await link.getAttribute('href');
  expect(href).toMatch(/^\/quadra\/\d{5}$/);

  // placar aberto na mesma sessão do navegador (admin): vê as duplas chegarem sem recarregar
  const placar = await p.context().newPage();
  await placar.goto(href);
  await placar.getByLabel(/Marcar ponto para/).first().waitFor();

  await expect(p.getByRole('button', { name: 'Chamar partida' })).toBeEnabled();
  await p.getByRole('button', { name: 'Chamar partida' }).click();
  await expect(p.getByRole('heading', { name: 'Partida em quadra' })).toBeVisible();
  await expect(p.getByText('chamada', { exact: true })).toBeVisible();
  await expect(p.getByRole('button', { name: 'Chamar partida' })).toHaveCount(0);
  await expect(p.getByRole('button', { name: 'Encerrar partida' })).toBeDisabled();
  await expect(p.getByText(/Em jogo no placar \(0 × 0\)/)).toBeVisible();

  // a primeira a chegar (Ana) joga a primeira partida: o nome dela está no placar
  const primeiro = nomes[0].split(' ')[0];
  await expect(placar.getByText(new RegExp(primeiro)).first()).toBeVisible();
  await expect(placar.getByText(/ \+ /).first()).toBeVisible();
  await sessaoLimpa(p);
});

test('quadra vinculada por código e indisponível quando some', async ({ abrir }) => {
  const p = await abrir();
  await sessaoLimpa(p);
  await chegam(p, SEIS);
  await rodadaConfirmada(p);
  const criada = await p.request.post('/api/quadras', { data: { apelido: 'Eli', nome: 'Existente' } });
  const { id } = await criada.json();
  await abrirTela(p);
  await p.getByLabel('Ou vincule uma quadra existente pelo código').fill('00000');
  await p.getByRole('button', { name: 'Vincular', exact: true }).click();
  await expect(p.getByRole('alert')).toContainText('não encontrada ou expirada');
  await p.getByLabel('Ou vincule uma quadra existente pelo código').fill(id);
  await p.getByRole('button', { name: 'Vincular', exact: true }).click();
  await expect(p.getByText(`Quadra ${id}`)).toBeVisible();
  await expect(p.getByRole('button', { name: 'Chamar partida' })).toBeEnabled();
  await p.getByRole('button', { name: 'Desvincular' }).click();
  await expect(p.getByText('Nenhuma quadra vinculada.')).toBeVisible();
});

test('dois aparelhos na sessão veem as mudanças sem atualizar', async ({ abrir }) => {
  const a = await abrir();
  await sessaoLimpa(a);
  await chegam(a, SEIS);
  const b = await abrir();
  await abrirTela(a);
  await abrirTela(b);
  await expect(a.getByText('Ao vivo')).toBeVisible();
  await expect(b.getByText('Ao vivo')).toBeVisible();

  // A sorteia: B passa a mostrar a proposta sozinho
  await a.getByRole('button', { name: 'Sortear duplas' }).click();
  await expect(a.getByRole('heading', { name: /Proposta 1/ })).toBeVisible();
  await expect(b.getByRole('heading', { name: /Proposta 1/ })).toBeVisible();

  // B confirma: A vira o painel da condução
  await b.getByRole('button', { name: 'Confirmar e iniciar' }).click();
  await expect(a.getByRole('heading', { name: 'Quadra do placar' })).toBeVisible();
  await expect(b.getByRole('heading', { name: 'Quadra do placar' })).toBeVisible();

  // A cancela: B volta ao sorteio
  await a.getByRole('button', { name: 'Cancelar rodada' }).click();
  await a.getByRole('button', { name: 'Sim, cancelar rodada' }).click();
  await expect(b.getByRole('heading', { name: 'Sortear a rodada' })).toBeVisible();
  await sessaoLimpa(a);
});

test('painel da condução sem violações axe', async ({ abrir }) => {
  const p = await abrir({ viewport: { width: 390, height: 844 } });
  await sessaoLimpa(p);
  await chegam(p, SEIS);
  await rodadaConfirmada(p);
  await abrirTela(p);
  await p.getByRole('heading', { name: 'Quadra do placar' }).waitFor();
  await p.evaluate(() => Promise.all(document.getAnimations().filter((a) => a.effect?.getTiming().iterations !== Infinity).map((a) => a.finished.catch(() => {}))));
  const { violations } = await new AxeBuilder({ page: p }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze();
  expect(violations.map((v) => `${v.id}: ${v.nodes.map((n) => n.target.join(' ') + ' ' + (n.any[0]?.message ?? '')).join(' | ')}`)).toEqual([]);
  await sessaoLimpa(p);
});

// Pontos pelo placar de verdade (mesma API da tela). O cookie do operador é
// `Secure` e só o navegador o envia por http, então a chamada sai da página.
async function pontosNoPlacar(p, codigo, equipe, quantos) {
  const statuses = await p.evaluate(async ([id, eq, n]) => {
    const quadra = await (await fetch(`/api/quadras/${id}`)).json();
    const saida = [];
    for (let i = 0; i < n; i += 1) {
      const r = await fetch(`/api/quadras/${id}/pontos`, {
        method: 'POST',
        headers: { 'content-type': 'application/json', 'x-control-version': String(quadra.controle_versao) },
        body: JSON.stringify({ equipe: eq }),
      });
      saida.push(r.status);
    }
    return saida;
  }, [codigo, equipe, quantos]);
  expect(statuses).toEqual(Array(quantos).fill(201));
}

async function criarEVincular(p) {
  await p.getByRole('button', { name: 'Criar quadra e vincular' }).click();
  const href = await p.getByRole('link', { name: 'Abrir o placar' }).getAttribute('href');
  return href.split('/').pop();
}

test('encerrar partida: placar ao vivo, fila andando, rei e fim da fila', async ({ abrir }) => {
  const p = await abrir();
  const b = await abrir();
  await sessaoLimpa(p);
  await chegam(p, SEIS);
  await rodadaConfirmada(p, 10);
  await abrirTela(p);
  await abrirTela(b);
  const codigo = await criarEVincular(p);

  // partida 1: Time 1 × Time 2
  await p.getByRole('button', { name: 'Chamar partida' }).click();
  await expect(p.getByRole('button', { name: 'Encerrar partida' })).toBeDisabled();
  await pontosNoPlacar(p, codigo, 'A', 4);
  await expect(p.getByText('Placar: 4 × 0')).toBeVisible(); // ao vivo, sem atualizar
  await expect(p.getByText('em jogo', { exact: true })).toBeVisible();
  await expect(p.getByText(/Em jogo no placar \(4 × 0\)/)).toBeVisible();
  await pontosNoPlacar(p, codigo, 'A', 6);
  await expect(p.getByText(/terminou — Time 1 venceu/)).toBeVisible();
  await expect(p.getByRole('button', { name: 'Encerrar partida' })).toBeEnabled();
  await p.getByRole('button', { name: 'Encerrar partida' }).click();

  await expect(p.getByRole('heading', { name: 'Partidas encerradas (1)' })).toBeVisible();
  await expect(p.getByText('Time 1 10 × 0 Time 2')).toBeVisible();
  await expect(p.getByRole('heading', { name: 'Eliminados (2)' })).toBeVisible();
  await expect(p.getByRole('status').filter({ hasText: 'Time 1 × Time 3' })).toBeVisible();
  // o outro aparelho acompanhou
  await expect(b.getByRole('heading', { name: 'Partidas encerradas (1)' })).toBeVisible();

  // partida 2: Time 1 × Time 3, vence o Time 3 (B): sobra um time sozinho → fim da fila
  await p.getByRole('button', { name: 'Chamar partida' }).click();
  await pontosNoPlacar(p, codigo, 'B', 10);
  await expect(p.getByRole('button', { name: 'Encerrar partida' })).toBeEnabled();
  await p.getByRole('button', { name: 'Encerrar partida' }).click();
  await expect(p.getByText(/A fase de fila terminou\. Time 3 abre o mata-mata/)).toBeVisible();
  await expect(p.getByRole('button', { name: 'Coroar campeão' })).toBeVisible();
  await expect(p.getByRole('button', { name: 'Chamar partida' })).toHaveCount(0);
  await expect(b.getByText(/A fase de fila terminou\. Time 3 abre o mata-mata/)).toBeVisible();

  // cancelar com partidas registradas pede confirmação reforçada
  await p.getByRole('button', { name: 'Cancelar rodada' }).click();
  await expect(p.getByText(/já tem 2 partida\(s\) registrada\(s\)/)).toBeVisible();
  await p.getByRole('button', { name: 'Voltar' }).click();
  await sessaoLimpa(p);
});

test('dois vencimentos seguidos coroam o rei e o painel mostra a ordem', async ({ abrir }) => {
  const p = await abrir();
  await sessaoLimpa(p);
  await chegam(p, [...SEIS, ['Gabi', 'M', 45], ['Hugo', 'H', 35]]); // 4 times
  await rodadaConfirmada(p, 10);
  await abrirTela(p);
  const codigo = await criarEVincular(p);
  for (const vencedor of ['A', 'A']) {
    await p.getByRole('button', { name: 'Chamar partida' }).click();
    await pontosNoPlacar(p, codigo, vencedor, 10);
    await expect(p.getByRole('button', { name: 'Encerrar partida' })).toBeEnabled();
    await p.getByRole('button', { name: 'Encerrar partida' }).click();
    await expect(p.getByRole('button', { name: 'Chamar partida' }).or(p.getByRole('button', { name: 'Iniciar mata-mata' }))).toBeVisible();
  }
  await expect(p.getByRole('heading', { name: 'Reis (1)' })).toBeVisible();
  await expect(p.getByText(/1º rei · Time 1/)).toBeVisible();
  await expect(p.getByRole('heading', { name: 'Partidas encerradas (2)' })).toBeVisible();
  await p.evaluate(() => Promise.all(document.getAnimations().filter((a) => a.effect?.getTiming().iterations !== Infinity).map((a) => a.finished.catch(() => {}))));
  const { violations } = await new AxeBuilder({ page: p }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze();
  expect(violations.map((v) => `${v.id}: ${v.nodes.map((n) => n.target.join(' ') + ' ' + (n.any[0]?.message ?? '')).join(' | ')}`)).toEqual([]);
  await sessaoLimpa(p);
});

test('mata-mata: iniciar, o rei desafia, ganhou ficou e o campeão aparece nos dois aparelhos', async ({ abrir }) => {
  const p = await abrir();
  const b = await abrir();
  await sessaoLimpa(p);
  await chegam(p, [...SEIS, ['Gabi', 'M', 45], ['Hugo', 'H', 35]]); // 4 times
  await rodadaConfirmada(p, 10);
  await abrirTela(p);
  await abrirTela(b);
  const codigo = await criarEVincular(p);
  // Time 1 vence duas seguidas (rei); o Time 4 sobra sozinho na quadra
  for (const vencedor of ['A', 'A']) {
    await p.getByRole('button', { name: 'Chamar partida' }).click();
    await pontosNoPlacar(p, codigo, vencedor, 10);
    await p.getByRole('button', { name: 'Encerrar partida' }).click();
    await expect(p.getByRole('button', { name: 'Chamar partida' }).or(p.getByRole('button', { name: 'Iniciar mata-mata' }))).toBeVisible();
  }
  await expect(p.getByText(/Time 4 abre o mata-mata contra Time 1/)).toBeVisible();
  await expect(p.getByRole('button', { name: 'Chamar partida' })).toHaveCount(0);
  await p.getByRole('button', { name: 'Iniciar mata-mata' }).click();
  await expect(p.getByRole('heading', { name: 'Próxima partida do mata-mata' })).toBeVisible();
  await expect(b.getByRole('heading', { name: 'Próxima partida do mata-mata' })).toBeVisible();
  await expect(p.getByRole('status').filter({ hasText: 'Time 4 × Time 1' })).toBeVisible();
  await p.evaluate(() => Promise.all(document.getAnimations().filter((a) => a.effect?.getTiming().iterations !== Infinity).map((a) => a.finished.catch(() => {}))));
  const { violations } = await new AxeBuilder({ page: p }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze();
  expect(violations.map((v) => `${v.id}: ${v.nodes.map((n) => n.target.join(' ') + ' ' + (n.any[0]?.message ?? '')).join(' | ')}`)).toEqual([]);

  await p.getByRole('button', { name: 'Chamar partida' }).click();
  await pontosNoPlacar(p, codigo, 'B', 10); // o rei (Time 1) vence o desafiante
  await p.getByRole('button', { name: 'Encerrar partida' }).click();
  await expect(p.getByRole('heading', { name: 'Campeões da rodada 1' })).toBeVisible();
  await expect(b.getByRole('heading', { name: 'Campeões da rodada 1' })).toBeVisible();
  await expect(p.getByText('Já dá para sortear a próxima.')).toBeVisible();
  await sessaoLimpa(p);
});

const IMPAR = [['Hugo', 'H', 60], ['Iris', 'M', 61], ['Joao', 'H', 62], ['Kely', 'M', 63], ['Luca', 'H', 64]];

test('time incompleto em quadra: escolher o parceiro, chamar e somar o saldo', async ({ abrir }) => {
  const p = await abrir();
  const b = await abrir();
  await sessaoLimpa(p);
  const nomes = await chegam(p, IMPAR); // Luca, o último a chegar, fica sem dupla
  await rodadaConfirmada(p, 10);
  await abrirTela(p);
  await abrirTela(b);
  const codigo = await criarEVincular(p);

  // 1ª partida: Time 1 vence o Time 2; o Time 3 (incompleto) entra em quadra
  await p.getByRole('button', { name: 'Chamar partida' }).click();
  await pontosNoPlacar(p, codigo, 'A', 10);
  await expect(p.getByRole('button', { name: 'Encerrar partida' })).toBeEnabled();
  await p.getByRole('button', { name: 'Encerrar partida' }).click();

  await expect(p.getByRole('heading', { name: 'Escolher o parceiro do Time 3' })).toBeVisible();
  await expect(b.getByRole('heading', { name: 'Escolher o parceiro do Time 3' })).toBeVisible();
  await expect(p.getByText('Escolha o parceiro do Time 3 antes de chamar a partida.')).toBeVisible();
  await expect(p.getByRole('button', { name: 'Chamar partida' })).toBeDisabled();
  // Luca é homem: só mulheres eliminadas aparecem
  const botoes = p.getByRole('button', { name: /^Escalar / });
  await expect(botoes).toHaveCount(1);
  await p.evaluate(() => Promise.all(document.getAnimations().filter((a) => a.effect?.getTiming().iterations !== Infinity).map((a) => a.finished.catch(() => {}))));
  const { violations } = await new AxeBuilder({ page: p }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']).analyze();
  expect(violations.map((v) => `${v.id}: ${v.nodes.map((n) => n.target.join(' ') + ' ' + (n.any[0]?.message ?? '')).join(' | ')}`)).toEqual([]);

  const escolhida = (await botoes.first().getAttribute('aria-label')).replace(/^Escalar (.*) com .*$/, '$1');
  expect([nomes[1], nomes[3]]).toContain(escolhida); // uma das mulheres
  await botoes.first().click();
  await expect(p.getByRole('heading', { name: 'Escolher o parceiro do Time 3' })).toHaveCount(0);
  await expect(b.getByRole('heading', { name: 'Escolher o parceiro do Time 3' })).toHaveCount(0);
  await expect(p.getByText(/· escalado/).first()).toBeVisible();
  await expect(p.getByRole('button', { name: 'Chamar partida' })).toBeEnabled();

  // 2ª partida: o time 3 (B) vence; a escalada soma as duas participações
  await p.getByRole('button', { name: 'Chamar partida' }).click();
  await pontosNoPlacar(p, codigo, 'B', 10);
  await expect(p.getByRole('button', { name: 'Encerrar partida' })).toBeEnabled();
  await p.getByRole('button', { name: 'Encerrar partida' }).click();
  await expect(p.getByRole('heading', { name: 'Saldo da rodada' })).toBeVisible();
  await expect(p.getByText(new RegExp(`${escolhida} \\(2 partidas\\)`))).toBeVisible();
  await sessaoLimpa(p);
});

// CV8.DS5.US13 — quem acompanha a quadra vê a fila e os reis ao vivo.
test('espectador vê a fila e os reis, e eles andam com as partidas', async ({ abrir }) => {
  const p = await abrir();
  const esp = await abrir();
  await sessaoLimpa(p);
  const nomes = await chegam(p, [...SEIS, ['Gabi', 'M', 45], ['Hugo', 'H', 35]]); // 4 times
  await rodadaConfirmada(p, 10);
  await abrirTela(p);
  const codigo = await criarEVincular(p);
  await entrarNaSala(esp, codigo);
  const faixa = esp.getByLabel('Fila e reis');
  await expect(faixa).toContainText('Fila:');
  await expect(faixa).toContainText('Reis: nenhum');
  for (let i = 0; i < 2; i++) {
    await p.getByRole('button', { name: 'Chamar partida' }).click();
    await pontosNoPlacar(p, codigo, 'A', 10);
    await p.getByRole('button', { name: 'Encerrar partida' }).click();
    await expect(p.getByRole('button', { name: 'Chamar partida' }).or(p.getByRole('button', { name: 'Iniciar mata-mata' }))).toBeVisible();
  }
  await expect(faixa).not.toContainText('Reis: nenhum');
  const primeiro = nomes[0].split(' ')[0];
  await expect(faixa).toContainText(primeiro);
  await sessaoLimpa(p);
});
