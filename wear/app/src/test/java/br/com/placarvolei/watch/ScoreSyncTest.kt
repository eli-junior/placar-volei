package br.com.placarvolei.watch

import kotlinx.coroutines.runBlocking
import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder

/**
 * Servidor falso com a regra de `/api/watch/comandos` que importa aqui: recibo
 * por id (reenvio devolve o mesmo resultado), partida atual e desfazer por alvo.
 */
private class FakeServer(var partida: String = "p1", val relogio: String = "w1") {
    var seq = 0
    val ativos = mutableListOf<Pair<Int, String>>()
    val recibos = mutableMapOf<String, JSONObject>()
    var efeitos = 0
    /** Grava o lance e perde a resposta, como uma queda de rede depois do commit. */
    var perderProximaResposta = false
    var online = true

    fun snapshot(): JSONObject = JSONObject()
        .put("partida_id", partida).put("seq", seq)
        .put("quadra", JSONObject().put("controle_versao", 1).put("controle_id", relogio))
        .put("estado_partida", JSONObject()
            .put("pontos_a", ativos.count { it.second == "A" })
            .put("pontos_b", ativos.count { it.second == "B" })
            .put("eventos_ativos_seq", JSONArray(ativos.map { it.first }))
            .put("equipes_ativas", JSONArray(ativos.map { it.second })))

    fun send(body: JSONObject): Pair<Int, JSONObject>? {
        if (!online) return null
        val id = body.getString("id")
        val recibo = recibos.getOrPut(id) { apply(body) }
        if (perderProximaResposta) {
            perderProximaResposta = false
            return null
        }
        return 200 to JSONObject().put("recibo", recibo).put("estado", snapshot())
    }

    private fun apply(body: JSONObject): JSONObject {
        val recibo = JSONObject().put("id", body.getString("id"))
        if (body.getString("partida_id") != partida) {
            return recibo.put("status", "RECUSADO").put("detalhe", "Uma nova partida começou.")
        }
        seq++
        efeitos++
        if (body.getString("acao") == ACAO_PONTO) {
            ativos += seq to body.getString("equipe")
        } else {
            val alvo = if (body.has("alvo_comando")) recibos.getValue(body.getString("alvo_comando")).getInt("evento_seq")
            else body.getInt("alvo_seq")
            check(ativos.last().first == alvo) { "alvo mudou" }
            ativos.removeAt(ativos.size - 1)
        }
        return recibo.put("status", "APLICADO").put("evento_seq", seq)
    }
}

class ScoreSyncTest {
    @get:Rule val folder = TemporaryFolder()

    private val file get() = folder.root.resolve("fila.json")

    private fun linked(server: FakeServer): ScoreSync {
        var n = 0
        return ScoreSync(CommandQueue(file)) { "00000000-0000-0000-0000-00000000000${n++}" }.apply {
            setParticipant(server.relogio)
            applySnapshot(server.snapshot())
        }
    }

    private fun ScoreSync.drain(server: FakeServer) = runBlocking {
        repeat(20) { if (sendNext { server.send(it) }.first == SendResult.OCIOSO) return@runBlocking }
    }

    private fun ScoreSync.shown() = predicted(score!!, pending)

    @Test
    fun localFeedbackFollowsPersistedTapsAndDoesNotReplayOnSyncOrReopen() = runBlocking {
        val server = FakeServer()
        val sync = linked(server)
        assertNull(sync.pointFeedback)
        server.online = false
        assertTrue(sync.tap("A"))
        assertEquals(PointFeedback(1, "A"), sync.pointFeedback)
        assertEquals("A", CommandQueue(file).load().commands.single().equipe)
        assertTrue(sync.tap("A"))
        assertEquals(PointFeedback(2, "A"), sync.pointFeedback)
        assertTrue(sync.tap("B"))
        val last = PointFeedback(3, "B")
        assertEquals(last, sync.pointFeedback)
        sync.drain(server)
        assertEquals(last, sync.pointFeedback)
        server.online = true
        server.perderProximaResposta = true
        sync.sendNext { server.send(it) }
        sync.drain(server)
        repeat(3) { sync.applySnapshot(server.snapshot()) }
        assertEquals(last, sync.pointFeedback)
        assertEquals(3, server.efeitos)
        assertNull(ScoreSync(CommandQueue(file)).pointFeedback)
        assertTrue(sync.undo())
        assertEquals(last, sync.pointFeedback)
    }

    @Test
    fun refusedTapAndDiskFailureDoNotGenerateFeedback() {
        val server = FakeServer()
        val sync = linked(server)
        val phone = server.snapshot().apply {
            getJSONObject("quadra").put("controle_id", "phone")
        }
        sync.applySnapshot(phone)
        assertFalse(sync.tap("A"))
        assertNull(sync.pointFeedback)
        sync.applySnapshot(server.snapshot())
        assertTrue(sync.tap("B"))
        val last = sync.pointFeedback
        // Um diretório no lugar do temporário força falha real de gravação.
        folder.root.resolve("fila.json.tmp").mkdir()
        assertFalse(sync.tap("A"))
        assertEquals(last, sync.pointFeedback)
        assertEquals(1, sync.pending.size)
        assertNotNull(sync.saveError)
    }

    @Test
    fun phoneControlShowsShortMessageAndBlocksCommandsUntilReturned() {
        val server = FakeServer()
        val sync = linked(server)
        val snapshot = server.snapshot()
        snapshot.getJSONObject("quadra").put("controle_id", "phone")
        sync.applySnapshot(snapshot)
        assertEquals("Controle no telefone.", sync.blockReason)
        assertFalse(sync.controlled)
        assertFalse(sync.tap("A"))
        assertFalse(sync.undo())
        assertTrue(sync.pending.isEmpty())
        sync.applySnapshot(server.snapshot())
        assertNull(sync.blockReason)
        assertTrue(sync.tap("A"))
    }

    @Test
    fun refusalDiscardsTheWholeQueueWithNotice() = runBlocking {
        val server = FakeServer()
        val sync = linked(server)
        sync.tap("A")
        sync.tap("B")
        sync.sendNext { 200 to JSONObject().put("recibo", JSONObject().put("status", "RECUSADO").put("detalhe", "O controle mudou."))
            .put("estado", server.snapshot()) }
        assertTrue(sync.pending.isEmpty())
        assertEquals("2 lances não enviados · placar mudou", sync.notice)
        assertNull(sync.blockReason)
        assertTrue(ScoreSync(CommandQueue(file)).pending.isEmpty())
        sync.dismissNotice()
        assertNull(sync.notice)
    }

    @Test
    fun controlTakenWhileOfflineDiscardsQueueNamingTheController() {
        val server = FakeServer()
        val sync = linked(server)
        server.online = false
        sync.tap("A")
        sync.tap("B")
        sync.undo()
        val snapshot = server.snapshot()
        snapshot.getJSONObject("quadra").put("controle_id", "p9")
        snapshot.put("participantes", JSONArray().put(JSONObject().put("id", "p9").put("apelido", "Ana")))
        sync.applySnapshot(snapshot)
        assertTrue(sync.pending.isEmpty())
        assertEquals("3 lances não enviados · controle com Ana", sync.notice)
        assertEquals("Controle no telefone.", sync.blockReason)
        assertEquals(0, server.efeitos)
    }

    @Test
    fun revokedLinkDiscardsQueue() = runBlocking {
        val sync = linked(FakeServer())
        sync.tap("A")
        val (result, _) = sync.sendNext { 401 to JSONObject().put("detail", "Vínculo revogado.") }
        assertEquals(SendResult.NAO_AUTORIZADO, result)
        assertTrue(sync.pending.isEmpty())
        assertEquals("1 lance não enviado · vínculo encerrado", sync.notice)
    }

    @Test
    fun queueHeldByOlderVersionIsDiscardedOnOpen() {
        val server = FakeServer()
        linked(server).tap("A")
        val queue = CommandQueue(file)
        queue.save(queue.load().copy(held = "Lance recusado."))
        val reopened = ScoreSync(queue)
        assertTrue(reopened.pending.isEmpty())
        assertNull(reopened.state.held)
        assertEquals("1 lance não enviado · placar mudou", reopened.notice)
    }

    @Test
    fun corruptQueueFlagsLostUntilDismissedAndKeepsScoring() {
        file.writeText("{corrompido")
        val server = FakeServer()
        val sync = linked(server)
        assertTrue(sync.lostQueue)
        assertTrue(sync.tap("A"))
        sync.dismissLostQueue()
        assertFalse(sync.lostQueue)
    }

    @Test
    fun transientRefusalsKeepTheCommandQueuedAndUnheld() = runBlocking {
        val server = FakeServer()
        val sync = linked(server)
        assertTrue(sync.tap("A"))
        for (status in listOf(408, 425, 429)) {
            val (result, _) = sync.sendNext { status to JSONObject().put("detail", "espere") }
            assertEquals(SendResult.ADIADO, result)
            assertNull(sync.notice)
            assertEquals(1, sync.pending.size)
        }
        sync.drain(server)
        assertEquals(0, sync.pending.size)
        assertEquals(1, server.efeitos)
    }

    @Test
    fun definitiveRefusalWithoutReceiptAlsoDiscards() = runBlocking {
        val sync = linked(FakeServer())
        assertTrue(sync.tap("B"))
        sync.sendNext { 422 to JSONObject().put("detail", "Lance inválido.") }
        assertTrue(sync.pending.isEmpty())
        assertEquals("1 lance não enviado · placar mudou", sync.notice)
    }

    @Test
    fun offlineTapsAndUndoSurviveRestartAndSyncOnce() {
        val server = FakeServer()
        val sync = linked(server)
        server.online = false
        assertTrue(sync.tap("A"))
        assertTrue(sync.tap("B"))
        assertTrue(sync.tap("A"))
        assertTrue(sync.undo())
        sync.drain(server)
        assertEquals(1 to 1, sync.shown())
        assertEquals(4, sync.pending.size)

        // App reaberto sem rede: placar, id do relógio e fila voltam do disco.
        val reopened = ScoreSync(CommandQueue(file))
        assertEquals(1 to 1, reopened.shown())
        assertEquals(4, reopened.pending.size)
        assertTrue(reopened.controlled)
        assertNull(reopened.blockReason)

        server.online = true
        reopened.drain(server)
        assertTrue(reopened.pending.isEmpty())
        assertEquals(4, server.efeitos)
        assertEquals(1 to 1, reopened.shown())
        assertEquals(1 to 1, reopened.score!!.pontosA to reopened.score!!.pontosB)
    }

    @Test
    fun lostResponseIsRecoveredWithoutDuplicate() {
        val server = FakeServer()
        val sync = linked(server)
        sync.tap("A")
        server.perderProximaResposta = true
        runBlocking { assertEquals(SendResult.SEM_REDE, sync.sendNext { server.send(it) }.first) }
        assertEquals(1, sync.pending.size)
        sync.drain(server)
        assertTrue(sync.pending.isEmpty())
        assertEquals(1, server.efeitos)
        assertEquals(1 to 0, sync.shown())
    }

    @Test
    fun commandsCarryTheSeqSeenAtTap() {
        val server = FakeServer()
        val sync = linked(server)
        sync.tap("A")
        sync.drain(server)
        sync.tap("B")
        assertEquals(listOf(1), sync.pending.map { it.baseSeq })
        assertEquals(1, sync.pending.first().toJson().getInt("base_seq"))
    }

    @Test
    fun withoutSnapshotThereIsNoOfflineMatch() {
        val sync = ScoreSync(CommandQueue(file))
        assertNull(sync.score)
        assertFalse(sync.tap("A"))
        assertTrue(sync.pending.isEmpty())
    }

    @Test
    fun queueOfPreviousMatchIsDiscardedNotAppliedToNewOne() {
        val server = FakeServer()
        val sync = linked(server)
        server.online = false
        sync.tap("A")
        server.online = true
        server.partida = "p2"
        sync.drain(server)
        assertEquals(0, server.efeitos)
        assertTrue(sync.pending.isEmpty())
        assertEquals("1 lance não enviado · nova partida", sync.notice)
        assertEquals("p2", ScoreSync(CommandQueue(file)).score!!.partidaId)
    }

    @Test
    fun webSocketConfirmationRemovesCommandOnce() {
        val server = FakeServer()
        val sync = linked(server)
        sync.tap("A")
        val id = sync.pending.single().id
        server.send(sync.pending.single().toJson())!!
        sync.applySnapshot(server.snapshot(), id)
        assertTrue(sync.pending.isEmpty())
        sync.drain(server)
        assertEquals(1, server.efeitos)
    }

    @Test
    fun resetForgetsPreviousCourt() {
        val server = FakeServer()
        val sync = linked(server)
        sync.tap("A")
        sync.reset()
        assertNull(sync.score)
        assertNull(ScoreSync(CommandQueue(file)).participantId)
        assertTrue(ScoreSync(CommandQueue(file)).pending.isEmpty())
    }
}
