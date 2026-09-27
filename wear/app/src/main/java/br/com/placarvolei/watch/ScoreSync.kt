package br.com.placarvolei.watch

import org.json.JSONObject
import java.util.UUID

/** Resultado de uma tentativa de envio do lance mais antigo da fila. */
enum class SendResult { OCIOSO, SEM_REDE, ADIADO, ENVIADO, NAO_AUTORIZADO }

/** Recusas HTTP que não dizem nada sobre o lance: tentar de novo mais tarde. */
private val TRANSIENT = setOf(408, 425, 429)

/**
 * Placar e fila do relógio sem Android (CV3.DS1.TS1): placar confirmado
 * persistido, lances com a base vista no toque e o envio em ordem. O
 * `WatchModel` cuida de tela, rede e vínculo; esta classe decide o que muda.
 */
class ScoreSync(private val queue: CommandQueue, private val newId: () -> String = { UUID.randomUUID().toString() }) {
    // Escritos no dispatcher de disco, lidos pela tela.
    @Volatile var state: QueueState = queue.load()
        private set
    @Volatile var score: Confirmed? = parse(state.snapshot)
        private set
    /** A fila gravada estava ilegível ao abrir: avisar até a pessoa dispensar. */
    var lostQueue: Boolean = state.corrupted
        private set

    fun dismissLostQueue() { lostQueue = false }

    /** Motivo da última falha ao gravar; o lance não foi aceito. */
    var saveError: String? = null
        private set

    val pending get() = state.commands
    val held get() = state.held
    val participantId get() = state.participantId

    /** O controle do placar está com este relógio. */
    val controlled get() = score?.controleId?.let { it == participantId } == true

    /** Por que o relógio não opera o placar agora (pontos e desfazer); null = opera. */
    val controlReason: String?
        get() {
            val s = score ?: return "Carregando placar…"
            held?.let { return it }
            if (s.controleId == null || s.controleId != participantId) {
                return "Controle no telefone. Peça ao admin para passar o controle."
            }
            return null
        }

    /** Por que os botões de ponto estão travados agora; null = pode marcar. */
    val blockReason: String?
        get() {
            controlReason?.let { return it }
            val s = score ?: return "Carregando placar…"
            if (s.encerrada) return "Partida encerrada."
            val (a, b) = predicted(s, pending)
            if (avaliarVitoria(a, b, s.alvo, s.vantagem, s.teto) != null) return "Fim de partida. Aguardando confirmação."
            return null
        }

    /** Ponto no topo da pilha prevista; null = nada para desfazer. */
    private val undoTarget get() = score?.let { stack(it, pending).lastOrNull() }

    /** Desfazer segue valendo com a vitória prevista ou a partida encerrada. */
    val canUndo get() = controlReason == null && undoTarget != null

    /** Equipe ("A"/"B") do ponto que o desfazer vai anular; null = nenhum. */
    val undoTeam get() = undoTarget?.equipe

    /** Grava o ponto antes de qualquer retorno visual. Devolve se foi aceito. */
    fun tap(equipe: String): Boolean {
        val s = score ?: return false
        if (blockReason != null) return false
        return enqueue(PendingCommand(newId(), s.partidaId, s.controleVersao, equipe, baseSeq = s.seq))
    }

    /** Grava o desfazer do ponto visto no topo, antes do retorno visual. */
    fun undo(): Boolean {
        val s = score ?: return false
        val target = undoTarget ?: return false
        if (!canUndo) return false
        return enqueue(PendingCommand(
            newId(), s.partidaId, s.controleVersao, null, ACAO_DESFAZER,
            alvoSeq = target.seq.takeIf { target.comando == null }, alvoComando = target.comando,
            baseSeq = s.seq,
        ))
    }

    private fun enqueue(command: PendingCommand) = save(state.copy(commands = state.commands + command))

    /** Snapshot do servidor (HTTP ou WebSocket); o lance que ele confirma sai da fila. */
    fun applySnapshot(json: JSONObject, appliedId: String? = null) {
        val next = Confirmed.fromSnapshot(json)
        val accepted = score?.accepts(next) != false
        val commands = state.commands.filterNot { appliedId != null && it.id == appliedId }
        if (!accepted && commands.size == state.commands.size) return
        if (accepted) score = next
        save(state.copy(commands = commands, snapshot = if (accepted) json.toString() else state.snapshot))
    }

    fun setParticipant(id: String?) {
        if (id != state.participantId) save(state.copy(participantId = id))
    }

    /** Descarte explícito dos lances retidos; o placar confirmado fica. */
    fun discardHeld() = save(state.copy(commands = emptyList(), held = null))

    /** Outra quadra: nada da anterior (fila, placar, id) vale mais. */
    fun reset() {
        if (save(QueueState())) score = null
    }

    /** Envia o lance mais antigo e aplica o recibo. `send` devolve null sem rede. */
    suspend fun sendNext(send: suspend (JSONObject) -> Pair<Int, JSONObject>?): Pair<SendResult, JSONObject?> {
        val next = state.commands.firstOrNull()
        if (next == null || state.held != null) return SendResult.OCIOSO to null
        val result = send(next.toJson())
        if (result == null || result.first >= 500) return SendResult.SEM_REDE to null
        // Tempo esgotado, cedo demais ou excesso de pedidos: passageiros. O
        // lance fica na fila e sai depois, sem descarte manual (CV5.DS2.TS2).
        if (result.first in TRANSIENT) return SendResult.ADIADO to null
        val (status, data) = result
        if (status == 401) return SendResult.NAO_AUTORIZADO to data
        // O snapshot pelo WebSocket pode ter tirado o lance da fila antes da resposta.
        val stillQueued = state.commands.any { it.id == next.id }
        if (data.has("recibo")) {
            data.optJSONObject("estado")?.let { applySnapshot(it) }
            val recibo = data.getJSONObject("recibo")
            if (!stillQueued) Unit
            else if (recibo.optString("status") == "APLICADO") {
                save(state.copy(commands = state.commands.filterNot { it.id == next.id }))
            } else {
                save(state.copy(held = recibo.optString("detalhe").ifBlank { "Lance recusado." }))
            }
        } else if (stillQueued) {
            save(state.copy(held = data.optString("detail", "Lance recusado.")))
        }
        return SendResult.ENVIADO to data
    }

    private fun save(next: QueueState): Boolean = try {
        queue.save(next)
        state = next
        saveError = null
        true
    } catch (e: Exception) {
        saveError = "Não foi possível guardar o lance no relógio."
        false
    }

    private fun parse(raw: String?) = raw?.let { runCatching { Confirmed.fromSnapshot(JSONObject(it)) }.getOrNull() }
}
