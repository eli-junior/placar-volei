// @ts-check
/**
 * Cliente da base de jogadores (CV8.DS1.US1). O servidor responde 404 para
 * segredo errado (mascara o endpoint); aqui isso vira "segredo recusado".
 */

export class ErroJogadores extends Error {
  /** @param {string} mensagem @param {number} status @param {string} [campo] */
  constructor(mensagem, status, campo) {
    super(mensagem);
    this.status = status;
    this.campo = campo;
  }
}

/**
 * Chamada JSON protegida pelo segredo do dono, para qualquer rota do
 * gerenciador (`/api/jogadores`, `/api/sessao`).
 * @param {string} segredo
 * @param {string} url
 * @param {{ metodo?: string, corpo?: object }} [opcoes]
 * @param {typeof fetch} [buscar]
 */
export async function chamarApi(segredo, url, opcoes = {}, buscar = globalThis.fetch) {
  const { metodo = 'GET', corpo } = opcoes;
  const resposta = await buscar(url, {
    method: metodo,
    headers: { 'x-owner-secret': segredo, ...(corpo ? { 'content-type': 'application/json' } : {}) },
    body: corpo ? JSON.stringify(corpo) : undefined,
  });
  if (resposta.ok) return resposta.json();
  if (resposta.status === 404) throw new ErroJogadores('Segredo recusado. Confira e tente de novo.', 404);
  if (resposta.status === 429) throw new ErroJogadores('Muitas tentativas incorretas. Aguarde um pouco.', 429);
  const dados = await resposta.json().catch(() => null);
  const detalhe = typeof dados?.detail === 'string' ? dados.detail : 'Não foi possível concluir.';
  throw new ErroJogadores(detalhe, resposta.status, dados?.erros?.[0]?.campo);
}

/** @param {string} segredo @param {string} caminho @param {{ metodo?: string, corpo?: object }} [opcoes] @param {typeof fetch} [buscar] */
export function chamarJogadores(segredo, caminho, opcoes = {}, buscar = globalThis.fetch) {
  return chamarApi(segredo, `/api/jogadores${caminho}`, opcoes, buscar);
}

/** @param {string} segredo @param {string} caminho @param {{ metodo?: string, corpo?: object }} [opcoes] @param {typeof fetch} [buscar] */
export function chamarSessao(segredo, caminho, opcoes = {}, buscar = globalThis.fetch) {
  return chamarApi(segredo, `/api/sessao${caminho}`, opcoes, buscar);
}

/** @param {string} segredo @param {string} caminho @param {{ metodo?: string, corpo?: object }} [opcoes] @param {typeof fetch} [buscar] */
export function chamarRodada(segredo, caminho, opcoes = {}, buscar = globalThis.fetch) {
  return chamarApi(segredo, `/api/rodada${caminho}`, opcoes, buscar);
}

/** Os dois primeiros times da fila (a primeira partida), ou null. */
export function primeiraPartida(times) {
  const fila = [...(times ?? [])].sort((a, b) => a.fila - b.fila);
  return fila.length >= 2 ? [fila[0], fila[1]] : null;
}

/** Ajuste da nota pelo saldo da sessão: " +8", " −3" ou "" quando não há (RN-14). */
export function ajusteDaNota(j) {
  const d = j.nota - (j.nota_base ?? j.nota);
  if (!d) return '';
  return d > 0 ? ` +${d}` : ` −${-d}`;
}

/** "Ana (90) + Bia (85)" para a linha de um time. */
export function descreverTime(time) {
  return time.jogadores.map((j) => `${j.nome} (${j.nota}${ajusteDaNota(j)})${j.escalado ? ' · escalado' : ''}`).join(' + ');
}

/** Qual combinação equivalente está na tela: "2 de 5" (tentativa começa em 0). */
export function posicaoDaCombinacao(rodada) {
  const total = Math.max(1, rodada.distintas ?? 1);
  return { atual: (rodada.tentativa % total) + 1, total };
}

/**
 * Nova ordem dos ids depois de mover `id` uma posição (`-1` sobe, `+1` desce).
 * Nos limites devolve a lista como está.
 * @param {string[]} ids @param {string} id @param {number} delta
 */
export function moverPosicao(ids, id, delta) {
  const de = ids.indexOf(id);
  const para = de + delta;
  if (de < 0 || para < 0 || para >= ids.length) return [...ids];
  const nova = [...ids];
  [nova[de], nova[para]] = [nova[para], nova[de]];
  return nova;
}

/**
 * Nova ordem dos ids depois de levar `id` para a posição `destino` (0 = primeiro).
 * Os demais mantêm a ordem relativa. Fora da faixa, a posição é limitada.
 * @param {string[]} ids @param {string} id @param {number} destino
 */
export function moverPara(ids, id, destino) {
  const de = ids.indexOf(id);
  if (de < 0) return [...ids];
  const nova = ids.filter(x => x !== id);
  nova.splice(Math.max(0, Math.min(nova.length, destino)), 0, id);
  return nova;
}

/** Quantos presentes faltam para o mínimo do sorteio (0 quando já basta). */
export function faltamParaSortear(presentes, minimo = 4) {
  return Math.max(0, minimo - presentes);
}

/** Ativos primeiro, depois inativos, em ordem alfabética sem acento. */
export function ordenarJogadores(lista) {
  const chave = (/** @type {string} */ n) => n.normalize('NFD').replace(/\p{M}/gu, '').toLowerCase();
  return [...lista].sort((a, b) => Number(b.ativo) - Number(a.ativo) || chave(a.nome).localeCompare(chave(b.nome)));
}

/** Lado maior de 480 px, sem ampliar; devolve inteiros ≥ 1. */
export function dimensoesReduzidas(largura, altura, maximo = 480) {
  const maior = Math.max(largura, altura);
  if (!(maior > 0)) return { largura: 1, altura: 1 };
  const fator = maior > maximo ? maximo / maior : 1;
  return { largura: Math.max(1, Math.round(largura * fator)), altura: Math.max(1, Math.round(altura * fator)) };
}

/** Duas iniciais para o avatar sem foto ("Ana Maria Souza" → "AS"). */
export function iniciais(nome) {
  const partes = String(nome ?? '').trim().split(/\s+/).filter(Boolean);
  if (!partes.length) return '?';
  const primeira = partes[0][0];
  const ultima = partes.length > 1 ? partes[partes.length - 1][0] : '';
  return (primeira + ultima).toLocaleUpperCase('pt-BR');
}

/**
 * Reduz a foto no aparelho e a converte para JPEG (o servidor só aceita JPEG
 * de até 256 KB). `ImageBitmap` respeita a orientação EXIF da câmera.
 * @param {Blob} arquivo
 * @returns {Promise<Blob>}
 */
export async function reduzirParaJpeg(arquivo, maximo = 480) {
  let imagem;
  try {
    imagem = await createImageBitmap(arquivo, { imageOrientation: 'from-image' });
  } catch {
    throw new ErroJogadores('Não foi possível ler essa imagem. Tente outra foto.', 0);
  }
  const { largura, altura } = dimensoesReduzidas(imagem.width, imagem.height, maximo);
  const tela = document.createElement('canvas');
  tela.width = largura;
  tela.height = altura;
  tela.getContext('2d').drawImage(imagem, 0, 0, largura, altura);
  imagem.close?.();
  for (const qualidade of [0.8, 0.6, 0.4]) {
    const blob = await new Promise((ok) => tela.toBlob(ok, 'image/jpeg', qualidade));
    if (blob && blob.size <= 256 * 1024) return blob;
  }
  throw new ErroJogadores('A foto ficou grande demais. Tente outra.', 0);
}

/** @param {string} segredo @param {string} id @param {Blob} jpeg @param {typeof fetch} [buscar] */
export async function enviarFoto(segredo, id, jpeg, buscar = globalThis.fetch) {
  const resposta = await buscar(`/api/jogadores/${id}/foto`, {
    method: 'PUT',
    headers: { 'x-owner-secret': segredo, 'content-type': 'image/jpeg' },
    body: jpeg,
  });
  if (resposta.ok) return resposta.json();
  const dados = await resposta.json().catch(() => null);
  throw new ErroJogadores(typeof dados?.detail === 'string' ? dados.detail : 'Não foi possível enviar a foto.', resposta.status, 'foto');
}

/** URL local da foto (o `<img>` não envia o cabeçalho do segredo). */
export async function baixarFoto(segredo, id, buscar = globalThis.fetch) {
  const resposta = await buscar(`/api/jogadores/${id}/foto`, { headers: { 'x-owner-secret': segredo } });
  if (!resposta.ok) return null;
  return URL.createObjectURL(await resposta.blob());
}

/** Ignora estado mais velho que o já mostrado (resposta HTTP × mensagem do WebSocket). */
export function estadoMaisNovo(atual, novo) {
  if (!novo) return atual;
  if (!atual) return novo;
  return (novo.revisao ?? 0) >= (atual.revisao ?? 0) ? novo : atual;
}

/** Rótulo curto da sincronia na tela da sessão. */
export function rotuloSincronia(conectado, online = true) {
  if (!online) return { chave: 'offline', rotulo: 'Sem rede' };
  return conectado ? { chave: 'conectado', rotulo: 'Ao vivo' } : { chave: 'reconectando', rotulo: 'Reconectando…' };
}

/** Cria uma quadra do placar neste navegador (o operador vira o admin dela). */
export async function criarQuadraDoPlacar(apelido, buscar = globalThis.fetch) {
  const resposta = await buscar('/api/quadras', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ apelido, nome: 'Quadra do dia' }),
  });
  const dados = await resposta.json().catch(() => null);
  if (!resposta.ok) throw new ErroJogadores(typeof dados?.detail === 'string' ? dados.detail : 'Não foi possível criar a quadra.', resposta.status);
  return dados.id;
}

/** Texto do que falta para sortear ("Faltam 6 presentes"), ou o aviso de que já dá. */
export function mensagemFaltam(faltam) {
  if (faltam <= 0) return 'Já dá para sortear.';
  return faltam === 1 ? 'Falta 1 presente para sortear.' : `Faltam ${faltam} presentes para sortear.`;
}
