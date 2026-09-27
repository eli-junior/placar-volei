// @ts-check
import { SILENCIO_MAXIMO_MS } from '../sync.js';

/**
 * Ciclo de vida do WebSocket da sala, sem Svelte (CV5.DS5.TS1): abrir,
 * vigiar o silêncio, reconectar com backoff e retomar ao voltar do segundo
 * plano. O `App.svelte` só decide o que fazer com cada mensagem.
 *
 * Regra que protege tudo: evento de um socket que não é mais o atual é
 * ignorado. Resposta atrasada de conexão velha não mexe no estado.
 *
 * @param {Object} opcoes
 * @param {(alvo: string) => WebSocket} opcoes.criarSocket
 * @param {(mensagem: any) => void} opcoes.aoMensagem mensagens da sala (PING já filtrado)
 * @param {() => void} opcoes.aoCair conexão perdida (fechada, com erro ou silenciosa)
 * @param {(codigo: number) => boolean} opcoes.aoFechar devolve false para não reconectar (4401, 4404)
 * @param {typeof setTimeout} [opcoes.agendar]
 * @param {typeof clearTimeout} [opcoes.cancelar]
 * @param {() => number} [opcoes.agora]
 * @param {() => number} [opcoes.aleatorio]
 * @param {number} [opcoes.silencioMaximo]
 */
export function criarConexao({
  criarSocket,
  aoMensagem,
  aoCair,
  aoFechar,
  agendar = setTimeout,
  cancelar = clearTimeout,
  agora = Date.now,
  aleatorio = Math.random,
  silencioMaximo = SILENCIO_MAXIMO_MS,
}) {
  /** @type {WebSocket | null} */
  let socket = null;
  /** @type {string | null} */
  let alvo = null;
  let tentativas = 0;
  let ultimaMensagem = 0;
  /** @type {ReturnType<typeof setTimeout> | undefined} */
  let timerReconexao;
  /** @type {ReturnType<typeof setTimeout> | undefined} */
  let vigia;

  /** @param {WebSocket} s */
  function vigiar(s) {
    ultimaMensagem = agora();
    cancelar(vigia);
    vigia = agendar(() => derrubar(s), silencioMaximo);
  }

  // Conexão meio aberta (Wi-Fi do ginásio, celular que voltou do bolso) não
  // dispara onclose: sem notícia do servidor, larga o socket e reconecta.
  /** @param {WebSocket} s */
  function derrubar(s) {
    if (socket !== s) return;
    socket = null;
    cancelar(vigia);
    aoCair();
    try { s.close(); } catch { /* já fechado */ }
    agendarReconexao();
  }

  // Backoff exponencial com jitter (CV2.DS2.TS1); zera só com ESTADO_INICIAL.
  function agendarReconexao() {
    if (alvo === null) return;
    const base = Math.min(1000 * Math.pow(1.5, tentativas), 15000);
    tentativas += 1;
    cancelar(timerReconexao);
    timerReconexao = agendar(abrir, Math.round(base + aleatorio() * 800));
  }

  function fecharAtual() {
    cancelar(timerReconexao);
    cancelar(vigia);
    const anterior = socket;
    socket = null;
    anterior?.close();
  }

  function abrir() {
    if (alvo === null) return;
    fecharAtual();
    const s = criarSocket(alvo);
    socket = s;
    vigiar(s);
    s.onmessage = evento => {
      if (socket !== s) return;
      vigiar(s);
      let mensagem;
      try { mensagem = JSON.parse(evento.data); } catch { return; }
      if (mensagem?.tipo === 'PING') return;
      aoMensagem(mensagem);
    };
    s.onclose = evento => {
      if (socket !== s) return;
      socket = null;
      cancelar(vigia);
      aoCair();
      if (aoFechar(evento.code) === false) return;
      agendarReconexao();
    };
    s.onerror = () => s.close();
  }

  return {
    /** @param {string} novoAlvo */
    conectar(novoAlvo) {
      alvo = novoAlvo;
      tentativas = 0;
      abrir();
    },
    desconectar() {
      alvo = null;
      tentativas = 0;
      fecharAtual();
    },
    /** A sala respondeu com o estado inicial: a próxima queda recomeça do backoff curto. */
    confirmar() {
      tentativas = 0;
    },
    /** Volta do segundo plano ou da rede: reconecta já, se preciso. */
    retomar() {
      if (alvo === null) return;
      const aberto = socket && socket.readyState === 1;
      if (aberto && agora() - ultimaMensagem <= silencioMaximo) return;
      if (socket) derrubar(socket);
      tentativas = 0;
      abrir();
    },
    get tentativas() {
      return tentativas;
    },
  };
}
