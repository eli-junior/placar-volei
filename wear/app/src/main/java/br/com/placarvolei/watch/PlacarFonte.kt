package br.com.placarvolei.watch

/**
 * O que a tela do placar precisa de uma fonte de placar (CV7.US2). O servidor
 * (`WatchModel`) e a quadra local do celular (`CelularSessao`) a implementam, e
 * a `ScoreScreen` desenha os dois do mesmo jeito: placar, fila durável, desfazer
 * previsto, aro de conexão e avisos de descarte.
 */
interface PlacarFonte {
    val score: Confirmed?
    /** Placar previsto: confirmado mais o efeito dos lances na fila. */
    val shown: Pair<Int, Int>?
    val labels: Pair<String, String>
    /** Por que os botões de ponto estão travados agora; null = pode marcar. */
    val blockReason: String?
    val pending: List<PendingCommand>
    val connection: Connection
    /** O controle do placar está com este relógio. */
    val controlled: Boolean
    val lastPointTeam: String?
    val showNewMatch: Boolean
    val canUndo: Boolean
    val canStartNewMatch: Boolean
    val undoSpoken: String
    val lostQueue: Boolean
    val discardNotice: String?
    val pointFeedback: PointFeedback?
    /** Rótulo do modo na tela ("Local"); null no servidor, que é o padrão. */
    val modoRotulo: String?

    fun tap(equipe: String, done: (Boolean) -> Unit)
    fun undo(done: (Boolean) -> Unit)
    fun startNewMatch(): Boolean
    fun dismissLostQueue()
    fun dismissDiscardNotice()
}
