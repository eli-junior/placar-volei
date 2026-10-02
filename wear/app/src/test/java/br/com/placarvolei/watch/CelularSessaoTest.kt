package br.com.placarvolei.watch

import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
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
import java.io.File

/** Celular falso: guarda o que o relógio mandou e responde como a ponte da CV7.TS3. */
private class CelularFalso : CanalCelular {
    val enviados = mutableListOf<JSONObject>()
    var online = true
    /** Corpo e status da próxima resposta; padrão: aplica o lance. */
    var responder: (JSONObject) -> Pair<Int, JSONObject> = { corpo ->
        201 to JSONObject()
            .put("recibo", JSONObject().put("id", corpo.getString("id")).put("status", "APLICADO").put("evento_seq", 1))
            .put("estado", estado(seq = 9, pontosA = 1, comando = corpo.getString("id")))
    }
    var pedidos = 0

    override suspend fun enviar(corpo: JSONObject, tempoMs: Long): Pair<Int, JSONObject>? {
        if (!online) return null
        enviados += corpo
        return responder(corpo)
    }

    override suspend fun pedirEstado() { pedidos++ }
}

private fun estado(
    partida: String = "p1", seq: Int = 1, pontosA: Int = 0, pontosB: Int = 0, aberta: Boolean? = true,
    encerrada: Boolean = false, comando: String? = null,
): JSONObject = JSONObject()
    .put("partida_id", partida).put("seq", seq)
    .put("quadra", JSONObject().put("id", "LOCAL").put("controle_versao", 1).put("controle_id", CelularProtocolo.ID_RELOGIO))
    .put("estado_partida", JSONObject()
        .put("pontos_a", pontosA).put("pontos_b", pontosB).put("alvo", 10).put("vantagem", true)
        .put("encerrada", encerrada)
        .put("equipe_a", "Equipe A").put("equipe_b", "Equipe B")
        .put("eventos_ativos_seq", JSONArray((2..(pontosA + pontosB + 1)).toList()))
        .put("equipes_ativas", JSONArray(List(pontosA) { "A" } + List(pontosB) { "B" })))
    .also { if (aberta != null) it.put("sala_aberta", aberta) }
    .also { if (comando != null) it.put("comando_id", comando) }

class CelularSessaoTest {
    @get:Rule val pasta = TemporaryFolder()
    private var hora = 1_000_000L
    private val celular = CelularFalso()

    private fun sessao(arquivo: File = File(pasta.root, "fila-celular.json")) = CelularSessao(
        CommandQueue(arquivo), celular, CoroutineScope(Dispatchers.Unconfined + Job()),
        agora = { hora }, disk = Dispatchers.Unconfined,
    )

    @Test
    fun `sala aberta e recente liga a quadra local e fechada desliga`() = runBlocking {
        val s = sessao()
        assertFalse(s.ativa)
        s.aplicarEstado(estado(aberta = true))
        assertTrue(s.ativa)
        assertEquals(Connection.CONECTADO, s.connection)
        s.aplicarEstado(estado(aberta = false, seq = 2))
        assertFalse(s.ativa)
    }

    @Test
    fun `celular sem a flag de sala aberta nao leva o relogio para a quadra local`() = runBlocking {
        val s = sessao()
        s.aplicarEstado(estado(aberta = null))
        assertFalse(s.ativa)
    }

    @Test
    fun `sem sinal de vida por mais que a vida a sala conta como fechada`() = runBlocking {
        val s = sessao()
        s.aplicarEstado(estado())
        assertTrue(s.ativa)
        hora += CelularSessao.VIDA_MS - 1
        s.reavaliar()
        assertTrue(s.ativa)
        hora += 2
        s.reavaliar()
        assertFalse(s.ativa)
        // Um sinal novo reabre.
        s.aplicarEstado(estado(seq = 2))
        assertTrue(s.ativa)
    }

    @Test
    fun `sinal vencido com lances na fila mantem a quadra local com o anel vermelho`() = runBlocking {
        val s = sessao()
        s.aplicarEstado(estado())
        s.tap("A") {}
        hora += CelularSessao.VIDA_MS + 1
        s.reavaliar()
        // Celular com a tela apagada: o relógio segue mostrando a partida e os pontos pendentes.
        assertTrue(s.ativa)
        assertEquals(Connection.SEM_CONEXAO, s.connection)
        assertEquals(1, s.pending.size)

        // Enviado o que faltava, sem sinal e sem fila o relógio volta ao servidor.
        celular.online = true
        s.enviarProximo()
        hora += CelularSessao.VIDA_MS + 1
        s.reavaliar()
        assertFalse(s.ativa)
    }

    @Test
    fun `celular que fechou a sala devolve ao servidor mesmo com lances na fila`() = runBlocking {
        val s = sessao()
        s.aplicarEstado(estado())
        s.tap("A") {}
        s.aplicarEstado(estado(aberta = false, seq = 2))
        assertFalse(s.ativa)
        // O lance continua guardado para quando a sala reabrir (ou descartado com aviso).
        assertEquals(1, s.pending.size)
    }

    @Test
    fun `estado velho que ficou no Data Layer nao liga a quadra local`() = runBlocking {
        val s = sessao()
        s.aplicarEstado(estado(), recebidoEm = hora - CelularSessao.VIDA_MS - 1)
        assertFalse(s.ativa)
    }

    @Test
    fun `o controle e sempre do relogio e o placar vem do estado do celular`() = runBlocking {
        val s = sessao()
        s.aplicarEstado(estado(pontosA = 3, pontosB = 1, seq = 5))
        assertTrue(s.controlled)
        assertNull(s.blockReason)
        assertEquals(3 to 1, s.shown)
        assertEquals("Local", s.modoRotulo)
    }

    @Test
    fun `toque entra na fila e o recibo do celular a esvazia com o placar novo`() = runBlocking {
        val s = sessao()
        s.aplicarEstado(estado())
        var aceito = false
        s.tap("A") { aceito = it }
        assertTrue(aceito)
        assertEquals(1, s.pending.size)
        assertEquals(1 to 0, s.shown)

        assertEquals(SendResult.ENVIADO, s.enviarProximo())
        assertEquals("ponto", celular.enviados.single().getString("acao"))
        assertEquals("A", celular.enviados.single().getString("equipe"))
        assertEquals(0, s.pending.size)
        assertEquals(9, s.score!!.seq)
        assertEquals(Connection.CONECTADO, s.connection)
    }

    @Test
    fun `celular fora de alcance mantem o lance na fila e a conexao vermelha`() = runBlocking {
        val s = sessao()
        s.aplicarEstado(estado())
        s.tap("B") {}
        celular.online = false
        assertEquals(SendResult.SEM_REDE, s.enviarProximo())
        assertEquals(1, s.pending.size)
        assertEquals(Connection.SEM_CONEXAO, s.connection)

        celular.online = true
        assertEquals(SendResult.ENVIADO, s.enviarProximo())
        assertEquals(0, s.pending.size)
        assertEquals(Connection.CONECTADO, s.connection)
    }

    @Test
    fun `a fila sobrevive a fechar o app e fica separada da do servidor`() = runBlocking {
        val arquivo = File(pasta.root, "fila-celular.json")
        val s = sessao(arquivo)
        s.aplicarEstado(estado())
        s.tap("A") {}
        val reaberta = sessao(arquivo)
        assertEquals(1, reaberta.pending.size)
        assertEquals("A", reaberta.pending.single().equipe)
        assertFalse(File(pasta.root, "fila-lances.json").exists())
    }

    @Test
    fun `lance de partida que acabou e descartado com aviso e o celular manda`() = runBlocking {
        val s = sessao()
        s.aplicarEstado(estado())
        s.tap("A") {}
        celular.responder = { corpo ->
            200 to JSONObject()
                .put("recibo", JSONObject().put("id", corpo.getString("id")).put("status", "RECUSADO")
                    .put("detalhe", "Uma nova partida começou. Este lance não vale para ela.").put("evento_seq", JSONObject.NULL))
                .put("estado", estado(partida = "p2", seq = 1))
        }
        s.enviarProximo()
        assertEquals(0, s.pending.size)
        assertNotNull(s.discardNotice)
        assertTrue(s.discardNotice!!.contains("nova partida"))
        assertEquals("p2", s.score!!.partidaId)
    }

    @Test
    fun `nova partida so depois do fim, com a fila vazia e o celular ao alcance`() = runBlocking {
        val s = sessao()
        s.aplicarEstado(estado(pontosA = 10, encerrada = true, seq = 12))
        assertTrue(s.showNewMatch)
        assertTrue(s.canStartNewMatch)

        celular.responder = { corpo ->
            201 to JSONObject()
                .put("recibo", JSONObject().put("id", corpo.getString("id")).put("status", "APLICADO"))
                .put("estado", estado(partida = "p2", seq = 1, comando = corpo.getString("id")))
        }
        assertTrue(s.startNewMatch())
        assertEquals("nova_partida", celular.enviados.single().getString("acao"))
        assertEquals("p2", s.score!!.partidaId)
        assertFalse(s.showNewMatch)
    }

    @Test
    fun `nova partida nao aparece com a partida em andamento nem sem conexao`() = runBlocking {
        val s = sessao()
        s.aplicarEstado(estado(pontosA = 4))
        assertFalse(s.showNewMatch)
        assertFalse(s.startNewMatch())

        val fim = sessao(File(pasta.root, "outra.json"))
        fim.aplicarEstado(estado(pontosA = 10, encerrada = true, seq = 12))
        celular.online = false
        fim.tap("A") {}                      // partida encerrada trava o toque
        assertFalse(fim.canStartNewMatch && fim.connection != Connection.CONECTADO)
        celular.enviados.clear()
        assertTrue(celular.enviados.isEmpty())
    }
}
