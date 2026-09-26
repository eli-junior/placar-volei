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
    fun queueOfPreviousMatchIsHeldNotAppliedToNewOne() {
        val server = FakeServer()
        val sync = linked(server)
        server.online = false
        sync.tap("A")
        server.online = true
        server.partida = "p2"
        sync.drain(server)
        assertEquals(0, server.efeitos)
        assertNotNull(sync.held)
        assertEquals(1, sync.pending.size)
        // Descartar tira só os lances; o placar confirmado da partida nova fica.
        sync.discardHeld()
        assertTrue(sync.pending.isEmpty())
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
