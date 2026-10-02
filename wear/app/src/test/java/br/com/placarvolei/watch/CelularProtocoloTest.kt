package br.com.placarvolei.watch

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.runBlocking
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class CelularProtocoloTest {
    private fun resposta(id: String, status: Int, extra: JSONObject = JSONObject()) =
        JSONObject(extra.toString()).put("id", id).put("status", status).toString().toByteArray()

    @Test
    fun `lance vai com o mesmo corpo do servidor`() {
        val corpo = PendingCommand("id-1", "p1", 1, "A", baseSeq = 3).toJson()
        val lido = JSONObject(String(CelularProtocolo.codificarComando(corpo)))
        assertEquals(corpo.toString(), lido.toString())
        assertEquals("A", lido.getString("equipe"))
    }

    @Test
    fun `resposta separa id e status do corpo que a ScoreSync consome`() {
        val recibo = JSONObject().put("recibo", JSONObject().put("id", "id-1").put("status", "APLICADO"))
        val (id, par) = CelularProtocolo.decodificarResposta(resposta("id-1", 201, recibo))!!
        assertEquals("id-1", id)
        assertEquals(201, par.first)
        assertEquals("APLICADO", par.second.getJSONObject("recibo").getString("status"))
        assertFalse(par.second.has("id") || par.second.has("status"))
    }

    @Test
    fun `resposta ilegivel ou sem id e descartada`() {
        assertNull(CelularProtocolo.decodificarResposta("{ nao".toByteArray()))
        assertNull(CelularProtocolo.decodificarResposta("""{"status":201}""".toByteArray()))
        assertNull(CelularProtocolo.decodificarResposta("""{"id":null,"status":400}""".toByteArray()))
    }

    @Test
    fun `estado so vale se for um snapshot legivel`() {
        val snapshot = JSONObject()
            .put("partida_id", "p1").put("seq", 4)
            .put("quadra", JSONObject().put("controle_versao", 1).put("controle_id", CelularProtocolo.ID_RELOGIO))
            .put("estado_partida", JSONObject().put("pontos_a", 2).put("pontos_b", 1))
        assertNotNull(CelularProtocolo.decodificarEstado(snapshot.toString().toByteArray()))
        assertNull(CelularProtocolo.decodificarEstado("{}".toByteArray()))
        assertNull(CelularProtocolo.decodificarEstado("lixo".toByteArray()))
    }

    @Test
    fun `a resposta que chega durante o envio encontra a espera`() = runBlocking {
        val respostas = RespostasEsperadas()
        // A resposta chega "antes" de enviar() terminar: a espera já estava registrada.
        val par = respostas.aguardar("id-1", 1_000) {
            assertTrue(respostas.entregar(resposta("id-1", 201)))
            true
        }
        assertEquals(201, par!!.first)
    }

    @Test
    fun `sem resposta a tempo devolve null e libera a espera`() = runBlocking {
        val respostas = RespostasEsperadas()
        assertNull(respostas.aguardar("id-1", 50) { true })
        // Resposta tardia a um lance que ninguém mais espera é ignorada.
        assertFalse(respostas.entregar(resposta("id-1", 201)))
    }

    @Test
    fun `sem celular ao alcance o envio nem espera`() = runBlocking {
        val respostas = RespostasEsperadas()
        assertNull(respostas.aguardar("id-1", 5_000) { false })
    }

    @Test
    fun `respostas de lances diferentes nao se misturam`() = runBlocking {
        val respostas = RespostasEsperadas()
        // Em outra thread: o laço abaixo espera com Thread.sleep e travaria o runBlocking.
        val a = async(Dispatchers.Default) { respostas.aguardar("a", 1_000) { true } }
        val b = async(Dispatchers.Default) { respostas.aguardar("b", 1_000) { true } }
        while (!respostas.entregar(resposta("b", 200))) Thread.sleep(5)
        while (!respostas.entregar(resposta("a", 409, JSONObject().put("detail", "x")))) Thread.sleep(5)
        assertEquals(200, b.await()!!.first)
        assertEquals(409, a.await()!!.first)
        assertEquals("x", a.await()!!.second.getString("detail"))
    }

    @Test
    fun `resposta duplicada para o mesmo lance so vale uma vez`() = runBlocking {
        val respostas = RespostasEsperadas()
        val par = async(Dispatchers.Default) { respostas.aguardar("id-1", 1_000) { true } }
        while (!respostas.entregar(resposta("id-1", 201))) Thread.sleep(5)
        assertEquals(201, par.await()!!.first)
        assertFalse(respostas.entregar(resposta("id-1", 201)))
    }
}
