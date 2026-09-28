package br.com.placarvolei.watch

/** Retorno efêmero de um toque gravado localmente; não significa aceite do servidor. */
internal data class PointFeedback(val sequence: Long, val team: String)
