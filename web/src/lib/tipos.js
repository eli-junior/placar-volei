// @ts-check
/**
 * Formas que o backend manda pelo WebSocket e pelo HTTP (CV5.DS5.TS1). Só
 * documentação para o `@ts-check` dos módulos; não há código aqui.
 *
 * @typedef {Object} Quadra
 * @property {string} id código de 5 dígitos
 * @property {string} nome
 * @property {string | null} [partida_id]
 * @property {string | null} [controle_id]
 * @property {number} [controle_versao]
 *
 * @typedef {Object} Participante
 * @property {string} id
 * @property {string} apelido
 * @property {'ADMIN' | 'CONTROLADOR' | 'ESPECTADOR'} papel
 * @property {boolean} [online]
 *
 * @typedef {Object} EstadoPartida
 * @property {number} pontos_a
 * @property {number} pontos_b
 * @property {string} [equipe_a]
 * @property {string} [equipe_b]
 * @property {number} [alvo]
 * @property {boolean} [vantagem]
 * @property {number | null} [teto]
 * @property {boolean} [encerrada]
 * @property {'A' | 'B' | null} [vencedor]
 *
 * @typedef {Object} Snapshot
 * @property {string} partida_id
 * @property {number} seq
 * @property {Quadra} quadra
 * @property {EstadoPartida} estado_partida
 * @property {Participante[]} participantes
 * @property {Array<Object>} [linha_do_tempo]
 */
export {};
