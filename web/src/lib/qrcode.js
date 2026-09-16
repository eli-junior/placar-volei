/**
 * Codificador de QR Code — CV2.DS4.US5.
 *
 * Por que escrito aqui em vez de instalado do npm:
 *
 * 1. O uso é um só e é fixo: uma URL curta (`https://host/quadra/12345`), em
 *    modo byte, lida por uma câmera de celular a meio metro de distância. As
 *    bibliotecas populares carregam modo kanji, ECI, exportação em canvas/PNG
 *    e tabelas das 40 versões — dezenas de KB para um caso que cabe em uma
 *    versão pequena.
 * 2. O placar precisa abrir rápido em 4G ruim na beira da quadra. Cada
 *    dependência de runtime entra no bundle inicial.
 * 3. Sem dependência nova, o `npm install` continua reprodutível offline e a
 *    superfície de auditoria do frontend não cresce.
 *
 * Escopo deliberado: modo **byte** (Latin-1/UTF-8), versões **1 a 10**, todos
 * os quatro níveis de correção. Isso cobre até 271 bytes no nível L e 213 no
 * nível M — muito acima de qualquer URL de sala. Conteúdo maior lança erro em
 * vez de degradar em silêncio.
 *
 * Referência: ISO/IEC 18004. As tabelas abaixo são as do padrão.
 */

/** Níveis de correção de erro, na ordem dos bits do campo de formato. */
export const NIVEIS = { L: 0, M: 1, Q: 2, H: 3 };

/**
 * Capacidade em códigos de dados (data codewords) por versão e nível.
 * Índice: [versao - 1][nivel] com nivel em L, M, Q, H.
 */
const CODIGOS_DE_DADOS = [
  [19, 16, 13, 9], // v1
  [34, 28, 22, 16], // v2
  [55, 44, 34, 26], // v3
  [80, 64, 48, 36], // v4
  [108, 86, 62, 46], // v5
  [136, 108, 76, 60], // v6
  [156, 124, 88, 66], // v7
  [194, 154, 110, 86], // v8
  [232, 182, 132, 100], // v9
  [274, 216, 154, 122], // v10
];

/**
 * Blocos de correção por versão e nível: [códigos de EC por bloco,
 * blocos do grupo 1, códigos de dados por bloco do grupo 1,
 * blocos do grupo 2, códigos de dados por bloco do grupo 2].
 */
const BLOCOS_EC = [
  // v1
  [[7, 1, 19, 0, 0], [10, 1, 16, 0, 0], [13, 1, 13, 0, 0], [17, 1, 9, 0, 0]],
  // v2
  [[10, 1, 34, 0, 0], [16, 1, 28, 0, 0], [22, 1, 22, 0, 0], [28, 1, 16, 0, 0]],
  // v3
  [[15, 1, 55, 0, 0], [26, 1, 44, 0, 0], [18, 2, 17, 0, 0], [22, 2, 13, 0, 0]],
  // v4
  [[20, 1, 80, 0, 0], [18, 2, 32, 0, 0], [26, 2, 24, 0, 0], [16, 4, 9, 0, 0]],
  // v5
  [[26, 1, 108, 0, 0], [24, 2, 43, 0, 0], [18, 2, 15, 2, 16], [22, 2, 11, 2, 12]],
  // v6
  [[18, 2, 68, 0, 0], [16, 4, 27, 0, 0], [24, 4, 19, 0, 0], [28, 4, 15, 0, 0]],
  // v7
  [[20, 2, 78, 0, 0], [18, 4, 31, 0, 0], [18, 2, 14, 4, 15], [26, 4, 13, 1, 14]],
  // v8
  [[24, 2, 97, 0, 0], [22, 2, 38, 2, 39], [22, 4, 18, 2, 19], [26, 4, 14, 2, 15]],
  // v9
  [[30, 2, 116, 0, 0], [22, 3, 36, 2, 37], [20, 4, 16, 4, 17], [24, 4, 12, 4, 13]],
  // v10
  [[18, 2, 68, 2, 69], [26, 4, 43, 1, 44], [24, 6, 19, 2, 20], [28, 6, 15, 2, 16]],
];

/** Centros dos padrões de alinhamento por versão (v1 não tem). */
const CENTROS_ALINHAMENTO = [
  [],
  [6, 18],
  [6, 22],
  [6, 26],
  [6, 30],
  [6, 34],
  [6, 22, 38],
  [6, 24, 42],
  [6, 26, 46],
  [6, 28, 50],
];

// --- Aritmética no corpo de Galois GF(256), polinômio 0x11D ---------------

const EXP = new Uint8Array(512);
const LOG = new Uint8Array(256);

{
  let x = 1;
  for (let i = 0; i < 255; i++) {
    EXP[i] = x;
    LOG[x] = i;
    x <<= 1;
    if (x & 0x100) x ^= 0x11d;
  }
  for (let i = 255; i < 512; i++) EXP[i] = EXP[i - 255];
}

function multiplicar(a, b) {
  if (a === 0 || b === 0) return 0;
  return EXP[LOG[a] + LOG[b]];
}

/** Polinômio gerador de `grau` códigos de correção. */
function polinomioGerador(grau) {
  let gerador = [1];
  for (let i = 0; i < grau; i++) {
    const proximo = new Array(gerador.length + 1).fill(0);
    for (let j = 0; j < gerador.length; j++) {
      proximo[j] ^= gerador[j];
      proximo[j + 1] ^= multiplicar(gerador[j], EXP[i]);
    }
    gerador = proximo;
  }
  return gerador;
}

/** Códigos de correção de erro de um bloco de dados. */
function codigosDeCorrecao(dados, quantidade) {
  const gerador = polinomioGerador(quantidade);
  const resto = new Array(quantidade).fill(0);
  for (const byte of dados) {
    const fator = byte ^ resto[0];
    resto.shift();
    resto.push(0);
    if (fator !== 0) {
      for (let i = 0; i < quantidade; i++) {
        resto[i] ^= multiplicar(gerador[i + 1], fator);
      }
    }
  }
  return resto;
}

// --- Codificação ----------------------------------------------------------

/** Converte texto em bytes UTF-8 sem depender de `TextEncoder`. */
export function paraBytesUtf8(texto) {
  const bytes = [];
  for (const caractere of String(texto)) {
    let ponto = caractere.codePointAt(0);
    if (ponto < 0x80) {
      bytes.push(ponto);
    } else if (ponto < 0x800) {
      bytes.push(0xc0 | (ponto >> 6), 0x80 | (ponto & 0x3f));
    } else if (ponto < 0x10000) {
      bytes.push(0xe0 | (ponto >> 12), 0x80 | ((ponto >> 6) & 0x3f), 0x80 | (ponto & 0x3f));
    } else {
      bytes.push(
        0xf0 | (ponto >> 18),
        0x80 | ((ponto >> 12) & 0x3f),
        0x80 | ((ponto >> 6) & 0x3f),
        0x80 | (ponto & 0x3f)
      );
    }
  }
  return bytes;
}

/** Menor versão (1..10) que comporta `quantidadeBytes` no nível dado. */
export function menorVersao(quantidadeBytes, nivel) {
  const indiceNivel = NIVEIS[nivel];
  for (let versao = 1; versao <= 10; versao++) {
    const contadorBits = versao < 10 ? 8 : 16;
    const bitsNecessarios = 4 + contadorBits + quantidadeBytes * 8;
    if (CODIGOS_DE_DADOS[versao - 1][indiceNivel] * 8 >= bitsNecessarios) {
      return versao;
    }
  }
  return null;
}

function montarFluxoDeBits(bytes, versao, nivel) {
  const indiceNivel = NIVEIS[nivel];
  const totalCodigos = CODIGOS_DE_DADOS[versao - 1][indiceNivel];
  const bits = [];
  const empurrar = (valor, quantidade) => {
    for (let i = quantidade - 1; i >= 0; i--) bits.push((valor >> i) & 1);
  };

  empurrar(0b0100, 4); // modo byte
  empurrar(bytes.length, versao < 10 ? 8 : 16);
  for (const byte of bytes) empurrar(byte, 8);

  // Terminador de até 4 bits e alinhamento em byte.
  const capacidadeBits = totalCodigos * 8;
  const terminador = Math.min(4, capacidadeBits - bits.length);
  empurrar(0, terminador);
  while (bits.length % 8 !== 0) bits.push(0);

  // Preenchimento alternado 0xEC / 0x11 até fechar a capacidade.
  const preenchimentos = [0xec, 0x11];
  let i = 0;
  while (bits.length < capacidadeBits) {
    empurrar(preenchimentos[i++ % 2], 8);
  }

  const codigos = [];
  for (let b = 0; b < bits.length; b += 8) {
    let byte = 0;
    for (let j = 0; j < 8; j++) byte = (byte << 1) | bits[b + j];
    codigos.push(byte);
  }
  return codigos;
}

/** Intercala blocos de dados e de correção conforme o padrão. */
function intercalar(codigos, versao, nivel) {
  const [ecPorBloco, blocos1, dados1, blocos2, dados2] = BLOCOS_EC[versao - 1][NIVEIS[nivel]];
  const blocosDeDados = [];
  const blocosDeEc = [];
  let posicao = 0;

  for (let i = 0; i < blocos1; i++) {
    const bloco = codigos.slice(posicao, posicao + dados1);
    posicao += dados1;
    blocosDeDados.push(bloco);
    blocosDeEc.push(codigosDeCorrecao(bloco, ecPorBloco));
  }
  for (let i = 0; i < blocos2; i++) {
    const bloco = codigos.slice(posicao, posicao + dados2);
    posicao += dados2;
    blocosDeDados.push(bloco);
    blocosDeEc.push(codigosDeCorrecao(bloco, ecPorBloco));
  }

  const resultado = [];
  const maiorBloco = Math.max(dados1, dados2);
  for (let i = 0; i < maiorBloco; i++) {
    for (const bloco of blocosDeDados) {
      if (i < bloco.length) resultado.push(bloco[i]);
    }
  }
  for (let i = 0; i < ecPorBloco; i++) {
    for (const bloco of blocosDeEc) resultado.push(bloco[i]);
  }
  return resultado;
}

// --- Matriz ---------------------------------------------------------------

function novaMatriz(tamanho) {
  return {
    modulos: Array.from({ length: tamanho }, () => new Array(tamanho).fill(false)),
    reservado: Array.from({ length: tamanho }, () => new Array(tamanho).fill(false)),
  };
}

function desenharQuadrado(matriz, linha, coluna, tamanho, padrao) {
  for (let l = 0; l < tamanho; l++) {
    for (let c = 0; c < tamanho; c++) {
      const y = linha + l;
      const x = coluna + c;
      if (y < 0 || x < 0 || y >= matriz.modulos.length || x >= matriz.modulos.length) continue;
      matriz.modulos[y][x] = padrao(l, c);
      matriz.reservado[y][x] = true;
    }
  }
}

function desenharPadroesFixos(matriz, versao) {
  const tamanho = matriz.modulos.length;

  // Localizadores + separadores (área de 8×8 em cada canto).
  const localizador = (l, c) => {
    const li = l - 1;
    const ci = c - 1;
    if (li < 0 || ci < 0 || li > 6 || ci > 6) return false; // separador
    const borda = li === 0 || li === 6 || ci === 0 || ci === 6;
    const centro = li >= 2 && li <= 4 && ci >= 2 && ci <= 4;
    return borda || centro;
  };
  desenharQuadrado(matriz, -1, -1, 9, localizador);
  desenharQuadrado(matriz, -1, tamanho - 8, 9, localizador);
  desenharQuadrado(matriz, tamanho - 8, -1, 9, localizador);

  // Temporizadores.
  for (let i = 8; i < tamanho - 8; i++) {
    const escuro = i % 2 === 0;
    matriz.modulos[6][i] = escuro;
    matriz.reservado[6][i] = true;
    matriz.modulos[i][6] = escuro;
    matriz.reservado[i][6] = true;
  }

  // Padrões de alinhamento.
  const centros = CENTROS_ALINHAMENTO[versao - 1];
  for (const linha of centros) {
    for (const coluna of centros) {
      const cantoLocalizador =
        (linha === 6 && coluna === 6) ||
        (linha === 6 && coluna === tamanho - 7) ||
        (linha === tamanho - 7 && coluna === 6);
      if (cantoLocalizador) continue;
      desenharQuadrado(matriz, linha - 2, coluna - 2, 5, (l, c) => {
        const d = Math.max(Math.abs(l - 2), Math.abs(c - 2));
        return d !== 1;
      });
    }
  }

  // Módulo escuro fixo.
  matriz.modulos[tamanho - 8][8] = true;
  matriz.reservado[tamanho - 8][8] = true;

  // Reserva da informação de formato.
  for (let i = 0; i < 9; i++) {
    if (!matriz.reservado[8][i]) matriz.reservado[8][i] = true;
    if (!matriz.reservado[i][8]) matriz.reservado[i][8] = true;
  }
  for (let i = 0; i < 8; i++) {
    matriz.reservado[8][tamanho - 1 - i] = true;
    matriz.reservado[tamanho - 1 - i][8] = true;
  }

  // Reserva da informação de versão (v7+).
  if (versao >= 7) {
    for (let i = 0; i < 6; i++) {
      for (let j = 0; j < 3; j++) {
        matriz.reservado[tamanho - 11 + j][i] = true;
        matriz.reservado[i][tamanho - 11 + j] = true;
      }
    }
  }
}

function colocarDados(matriz, codigos) {
  const tamanho = matriz.modulos.length;
  const bits = [];
  for (const codigo of codigos) {
    for (let i = 7; i >= 0; i--) bits.push((codigo >> i) & 1);
  }

  let indice = 0;
  let subindo = true;
  for (let colunaBase = tamanho - 1; colunaBase > 0; colunaBase -= 2) {
    if (colunaBase === 6) colunaBase--; // pula a coluna do temporizador
    for (let passo = 0; passo < tamanho; passo++) {
      const linha = subindo ? tamanho - 1 - passo : passo;
      for (let deslocamento = 0; deslocamento < 2; deslocamento++) {
        const coluna = colunaBase - deslocamento;
        if (matriz.reservado[linha][coluna]) continue;
        matriz.modulos[linha][coluna] = indice < bits.length ? bits[indice++] === 1 : false;
      }
    }
    subindo = !subindo;
  }
}

const MASCARAS = [
  (l, c) => (l + c) % 2 === 0,
  (l) => l % 2 === 0,
  (_l, c) => c % 3 === 0,
  (l, c) => (l + c) % 3 === 0,
  (l, c) => (Math.floor(l / 2) + Math.floor(c / 3)) % 2 === 0,
  (l, c) => ((l * c) % 2) + ((l * c) % 3) === 0,
  (l, c) => (((l * c) % 2) + ((l * c) % 3)) % 2 === 0,
  (l, c) => (((l + c) % 2) + ((l * c) % 3)) % 2 === 0,
];

/**
 * Penalidade do padrão (regras N1..N4 do ISO/IEC 18004, §8.8.2).
 *
 * A nota decide qual das oito máscaras é aplicada. Ela não afeta a validade de
 * um símbolo já gerado — qualquer máscara produz um QR legível —, mas afeta o
 * quanto o leitor sofre para achar o símbolo em cima do painel da quadra. Por
 * isso a implementação segue o algoritmo do padrão à risca, e não uma
 * aproximação: o teste compara a matriz final com a da implementação de
 * referência, e máscara diferente significa matriz inteira diferente.
 *
 * As quatro regras:
 *
 * - **N1** — sequência de 5 ou mais módulos da mesma cor em linha ou coluna:
 *   3 pontos pelos cinco primeiros e 1 ponto por módulo adicional.
 * - **N2** — cada bloco 2×2 de mesma cor: 3 pontos.
 * - **N3** — trecho com a proporção do localizador (n:n:3n:n:n) tendo 4n
 *   módulos claros de um dos lados: 40 pontos por ocorrência, contada de cada
 *   lado separadamente. A proporção é escalável (n ≥ 1), não apenas 1:1:3:1:1,
 *   e a margem clara fora do símbolo conta como espaço claro.
 * - **N4** — desvio da proporção de módulos escuros em relação a 50%:
 *   10 pontos por faixa de 5 pontos percentuais de desvio.
 */
export function penalidade(modulos) {
  const tamanho = modulos.length;
  let total = 0;

  // N1 e N3 percorrem linhas e colunas compartilhando o mesmo histórico de
  // sequências: N1 conta o comprimento, N3 lê a proporção das últimas sete.
  for (const porLinha of [true, false]) {
    for (let i = 0; i < tamanho; i++) {
      const historico = [0, 0, 0, 0, 0, 0, 0];
      let corAtual = false; // a varredura começa comparando com claro
      let sequencia = 0;
      for (let j = 0; j < tamanho; j++) {
        const modulo = porLinha ? modulos[i][j] : modulos[j][i];
        if (modulo === corAtual) {
          sequencia++;
          if (sequencia === 5) total += 3;
          else if (sequencia > 5) total += 1;
        } else {
          empurrarHistorico(sequencia, historico, tamanho);
          if (!corAtual) total += contarPadroesDeLocalizador(historico) * 40;
          corAtual = modulo;
          sequencia = 1;
        }
      }
      total += encerrarHistorico(corAtual, sequencia, historico, tamanho) * 40;
    }
  }

  // N2: blocos 2×2 de mesma cor.
  for (let l = 0; l < tamanho - 1; l++) {
    for (let c = 0; c < tamanho - 1; c++) {
      const v = modulos[l][c];
      if (v === modulos[l][c + 1] && v === modulos[l + 1][c] && v === modulos[l + 1][c + 1]) {
        total += 3;
      }
    }
  }

  // N4: desvio da proporção de módulos escuros em relação a 50%.
  let escuros = 0;
  for (const linha of modulos) for (const modulo of linha) if (modulo) escuros++;
  const modulosTotais = tamanho * tamanho;
  const faixas = Math.ceil(Math.abs(escuros * 20 - modulosTotais * 10) / modulosTotais) - 1;
  total += faixas * 10;

  return total;
}

/**
 * Empurra uma sequência para o histórico das últimas sete.
 *
 * Na primeira inserção da varredura o histórico ainda está zerado: é o momento
 * em que a margem clara à esquerda (ou acima) do símbolo precisa ser somada,
 * porque para o leitor ela é espaço claro contínuo.
 */
function empurrarHistorico(sequencia, historico, tamanho) {
  const comprimento = historico[0] === 0 ? sequencia + tamanho : sequencia;
  historico.pop();
  historico.unshift(comprimento);
}

/**
 * Quantas vezes o histórico contém a proporção do localizador com 4n módulos
 * claros de um dos lados. Os dois lados são contados separadamente, como manda
 * o padrão: um trecho cercado de claro dos dois lados vale 80 pontos.
 */
function contarPadroesDeLocalizador(historico) {
  const n = historico[1];
  const nucleo =
    n > 0 &&
    historico[2] === n &&
    historico[3] === n * 3 &&
    historico[4] === n &&
    historico[5] === n;
  if (!nucleo) return 0;
  return (
    (historico[0] >= n * 4 && historico[6] >= n ? 1 : 0) +
    (historico[6] >= n * 4 && historico[0] >= n ? 1 : 0)
  );
}

/**
 * Fecha a linha ou coluna somando a margem clara à direita (ou abaixo) do
 * símbolo, e devolve as ocorrências de N3 que só aparecem no fechamento.
 */
function encerrarHistorico(corAtual, sequencia, historico, tamanho) {
  let corrente = sequencia;
  if (corAtual) {
    empurrarHistorico(corrente, historico, tamanho);
    corrente = 0;
  }
  corrente += tamanho; // margem clara depois do símbolo
  empurrarHistorico(corrente, historico, tamanho);
  return contarPadroesDeLocalizador(historico);
}

/**
 * Bits do nível no campo de formato. A ordem NÃO é a das tabelas de
 * capacidade: o padrão codifica L=01, M=00, Q=11, H=10.
 */
const NIVEL_NO_FORMATO = { L: 0b01, M: 0b00, Q: 0b11, H: 0b10 };

function bitsDeFormato(nivel, mascara) {
  const dados = (NIVEL_NO_FORMATO[nivel] << 3) | mascara;
  let valor = dados << 10;
  for (let i = 4; i >= 0; i--) {
    if (valor & (1 << (i + 10))) valor ^= 0b10100110111 << i;
  }
  return ((dados << 10) | valor) ^ 0b101010000010010;
}

function bitsDeVersao(versao) {
  let valor = versao << 12;
  for (let i = 5; i >= 0; i--) {
    if (valor & (1 << (i + 12))) valor ^= 0b1111100100101 << i;
  }
  return (versao << 12) | valor;
}

function escreverFormato(modulos, nivel, mascara) {
  const tamanho = modulos.length;
  const formato = bitsDeFormato(nivel, mascara);
  const bit = (i) => ((formato >> i) & 1) === 1;

  // Primeira cópia, em volta do localizador superior esquerdo: os bits 0..8
  // descem pela COLUNA 8 e os bits 9..14 seguem pela LINHA 8 em direção à
  // borda esquerda. A orientação importa: escrever a cópia transposta produz
  // um símbolo que qualquer leitor rejeita, porque ele lê o formato nestas
  // posições exatas antes de saber a máscara.
  for (let i = 0; i <= 5; i++) modulos[i][8] = bit(i);
  modulos[7][8] = bit(6);
  modulos[8][8] = bit(7);
  modulos[8][7] = bit(8);
  for (let i = 9; i <= 14; i++) modulos[8][14 - i] = bit(i);

  // Segunda cópia: bits 0..7 na LINHA 8 junto ao localizador superior direito
  // e bits 8..14 na COLUNA 8 junto ao localizador inferior esquerdo.
  for (let i = 0; i <= 7; i++) modulos[8][tamanho - 1 - i] = bit(i);
  for (let i = 8; i <= 14; i++) modulos[tamanho - 15 + i][8] = bit(i);

  modulos[tamanho - 8][8] = true; // módulo escuro permanente
}

function escreverVersao(modulos, versao) {
  if (versao < 7) return;
  const tamanho = modulos.length;
  const valor = bitsDeVersao(versao);
  for (let i = 0; i < 18; i++) {
    const escuro = ((valor >> i) & 1) === 1;
    const linha = Math.floor(i / 3);
    const coluna = tamanho - 11 + (i % 3);
    modulos[linha][coluna] = escuro;
    modulos[coluna][linha] = escuro;
  }
}

/**
 * Gera a matriz de módulos de um QR Code.
 *
 * @param {string} texto conteúdo (tipicamente a URL da sala)
 * @param {{ nivel?: 'L'|'M'|'Q'|'H' }} opcoes
 * @returns {{ versao: number, nivel: string, mascara: number, tamanho: number,
 *             modulos: boolean[][] }}
 */
export function gerarQrCode(texto, { nivel = 'M' } = {}) {
  if (!(nivel in NIVEIS)) {
    throw new Error(`Nível de correção desconhecido: ${nivel}`);
  }
  const bytes = paraBytesUtf8(texto);
  if (bytes.length === 0) {
    throw new Error('Não é possível gerar QR Code de conteúdo vazio.');
  }
  const versao = menorVersao(bytes.length, nivel);
  if (!versao) {
    throw new Error(
      `Conteúdo grande demais para o codificador (${bytes.length} bytes, máximo da versão 10).`
    );
  }

  const codigos = intercalar(montarFluxoDeBits(bytes, versao, nivel), versao, nivel);
  const tamanho = versao * 4 + 17;

  let melhor = null;
  for (let mascara = 0; mascara < 8; mascara++) {
    const matriz = novaMatriz(tamanho);
    desenharPadroesFixos(matriz, versao);
    colocarDados(matriz, codigos);
    for (let l = 0; l < tamanho; l++) {
      for (let c = 0; c < tamanho; c++) {
        if (!matriz.reservado[l][c] && MASCARAS[mascara](l, c)) {
          matriz.modulos[l][c] = !matriz.modulos[l][c];
        }
      }
    }
    escreverFormato(matriz.modulos, nivel, mascara);
    escreverVersao(matriz.modulos, versao);
    const nota = penalidade(matriz.modulos);
    if (!melhor || nota < melhor.nota) {
      melhor = { nota, mascara, modulos: matriz.modulos };
    }
  }

  return {
    versao,
    nivel,
    mascara: melhor.mascara,
    tamanho,
    modulos: melhor.modulos,
  };
}

/**
 * Caminho SVG (`d`) com todos os módulos escuros, um retângulo por módulo.
 * Um caminho único mantém o SVG pequeno e evita milhares de nós no DOM.
 *
 * @param {boolean[][]} modulos
 * @param {number} margem margem clara em módulos (o padrão manda 4)
 */
export function caminhoSvg(modulos, margem = 4) {
  const partes = [];
  for (let l = 0; l < modulos.length; l++) {
    for (let c = 0; c < modulos.length; c++) {
      if (modulos[l][c]) partes.push(`M${c + margem} ${l + margem}h1v1h-1z`);
    }
  }
  return partes.join('');
}

/** Lado do SVG em módulos, já com as duas margens. */
export function ladoComMargem(tamanho, margem = 4) {
  return tamanho + margem * 2;
}
