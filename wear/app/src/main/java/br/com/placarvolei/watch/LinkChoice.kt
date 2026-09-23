package br.com.placarvolei.watch

/**
 * Um vínculo por vez (CV3.DS1.US5). Ao abrir o app com vínculo guardado, o
 * relógio pergunta: retornar à quadra ou gerar um código novo, que substitui o
 * vínculo atual só quando for aprovado no telefone.
 */
enum class Stage { ABERTURA, CONFIRMAR_TROCA, CODIGO_NOVO, PLACAR }

/** O que o servidor disse do vínculo guardado, na tela de abertura. */
enum class LinkCheck { VERIFICANDO, VALIDO, SEM_REDE }

/**
 * Etapa ao criar a atividade. Um código novo à espera (app fechado com o
 * código na tela) volta a ser mostrado; uma desistência ainda não confirmada
 * pelo servidor não prende o relógio no código.
 */
fun openingStage(hasLink: Boolean, hasPendingCode: Boolean, cancelling: Boolean): Stage = when {
    hasPendingCode && !cancelling -> Stage.CODIGO_NOVO
    hasLink -> Stage.ABERTURA
    else -> Stage.PLACAR
}

fun returnLabel(court: String?, verb: String = "Retornar") =
    if (court.isNullOrBlank()) "$verb à quadra" else "$verb à quadra $court"

/** Aviso antes de gerar o código novo; null = nenhum lance a abandonar. */
fun abandonWarning(pending: Int, court: String?): String? {
    if (pending <= 0) return null
    val lances = if (pending == 1) "1 lance" else "$pending lances"
    val quadra = if (court.isNullOrBlank()) "desta quadra" else "da quadra $court"
    val verbo = if (pending == 1) "ainda não foi enviado" else "ainda não foram enviados"
    val fim = if (pending == 1) "ele será abandonado" else "eles serão abandonados"
    return "$lances $quadra $verbo. Se o novo código for aprovado, $fim."
}
