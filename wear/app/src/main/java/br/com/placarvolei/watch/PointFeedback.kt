package br.com.placarvolei.watch

/** Retorno efêmero de um toque gravado localmente; não significa aceite do servidor. */
data class PointFeedback(val sequence: Long, val team: String)
