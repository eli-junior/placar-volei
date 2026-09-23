package br.com.placarvolei.watch

import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class ScoreboardTest {
    private fun confirmed(
        a: Int = 0, b: Int = 0, equipeA: String = "Equipe A", equipeB: String = "Equipe B",
        jogadoresA: List<String> = emptyList(), jogadoresB: List<String> = emptyList(),
        partida: String = "p1", seq: Int = 1, ativos: List<Pair<Int, String>> = emptyList(),
    ) = Confirmed(partida, seq, 1, "eli", a, b, 12, true, null, false, equipeA, equipeB, jogadoresA, jogadoresB, ativos)

    private fun ponto(id: String, equipe: String, partida: String = "p1") = PendingCommand(id, partida, 1, equipe)
    private fun desfazer(id: String, partida: String = "p1") = PendingCommand(id, partida, 1, null, ACAO_DESFAZER)

    @Test
    fun victoryRuleMirrorsServer() {
        assertNull(avaliarVitoria(11, 10, 12, true, null))
        assertNull(avaliarVitoria(12, 11, 12, true, null))
        assertEquals("A", avaliarVitoria(12, 10, 12, true, null))
        assertEquals("B", avaliarVitoria(12, 14, 12, true, null))
        // Teto encerra sem a vantagem de dois.
        assertEquals("A", avaliarVitoria(15, 14, 12, true, 15))
        assertNull(avaliarVitoria(14, 14, 12, true, 15))
        // Sem vantagem, basta chegar ao alvo à frente.
        assertEquals("B", avaliarVitoria(11, 12, 12, false, null))
        assertNull(avaliarVitoria(12, 12, 12, false, null))
    }

    @Test
    fun defaultNamesShowUsAndThem() {
        assertEquals("Nós" to "Eles", teamLabels(confirmed()))
    }

    @Test
    fun playersBecomeInitials() {
        val c = confirmed(jogadoresA = listOf("Eli Junior", "Camila"), jogadoresB = listOf("Rafa", "Marvin"),
            equipeA = "Eli Junior / Camila", equipeB = "Rafa / Marvin")
        assertEquals("EC" to "RM", teamLabels(c))
    }

    @Test
    fun teamNameWithoutPlayersUsesWordInitialsOrTwoLetters() {
        assertEquals("TA" to "LO", teamLabels(confirmed(equipeA = "Time Azul", equipeB = "Lobos")))
    }

    @Test
    fun equalInitialsFallBackToUsAndThem() {
        val c = confirmed(jogadoresA = listOf("Eli", "Camila"), jogadoresB = listOf("Edu", "Carla"))
        assertEquals("Nós" to "Eles", teamLabels(c))
    }

    @Test
    fun onlyOneCustomTeamFallsBackToUsAndThem() {
        assertEquals("Nós" to "Eles", teamLabels(confirmed(jogadoresB = listOf("Rafa", "Marvin"))))
    }

    @Test
    fun predictedAddsOnlyPendingOfSameMatch() {
        val pending = listOf(
            PendingCommand("1", "p1", 1, "A"), PendingCommand("2", "p1", 1, "A"),
            PendingCommand("3", "p1", 1, "B"), PendingCommand("4", "antiga", 1, "B"),
        )
        assertEquals(4 to 2, predicted(confirmed(a = 2, b = 1), pending))
    }

    @Test
    fun undoPopsTopOfConfirmedPlusPending() {
        // Confirmado: A (seq 3), B (seq 4). Fila: A, desfazer, desfazer.
        val c = confirmed(a = 1, b = 1, ativos = listOf(3 to "A", 4 to "B"))
        val pending = listOf(ponto("x", "A"), desfazer("u1"), desfazer("u2"))
        assertEquals(listOf(StackPoint("A", seq = 3)), stack(c, pending))
        assertEquals(1 to 0, predicted(c, pending))
    }

    @Test
    fun topIsPendingCommandOrConfirmedSeq() {
        val c = confirmed(a = 1, ativos = listOf(3 to "A"))
        assertEquals(StackPoint("B", comando = "x"), stack(c, listOf(ponto("x", "B"))).last())
        assertEquals(StackPoint("A", seq = 3), stack(c, emptyList()).last())
    }

    @Test
    fun undoWithEmptyStackChangesNothing() {
        val c = confirmed()
        assertTrue(stack(c, listOf(desfazer("u"))).isEmpty())
        assertEquals(0 to 0, predicted(c, listOf(desfazer("u"))))
    }

    @Test
    fun pendingOfPreviousMatchIsIgnoredInStack() {
        val c = confirmed(a = 1, ativos = listOf(3 to "A"))
        assertEquals(1 to 0, predicted(c, listOf(ponto("x", "B", "antiga"), desfazer("u", "antiga"))))
    }

    @Test
    fun olderSnapshotIsIgnoredButNewMatchIsAccepted() {
        val current = confirmed(seq = 5)
        assertFalse(current.accepts(confirmed(seq = 4)))
        assertTrue(current.accepts(confirmed(seq = 5)))
        assertTrue(current.accepts(confirmed(seq = 1, partida = "p2")))
    }

    @Test
    fun parsesServerSnapshot() {
        val json = JSONObject("""
            {"partida_id": "p9", "seq": 7,
             "quadra": {"controle_id": "relogio-id", "controle_versao": 3},
             "estado_partida": {"pontos_a": 2, "pontos_b": 1, "alvo": 15, "vantagem": false, "teto": null,
               "encerrada": false, "equipe_a": "Eli / Camila", "equipe_b": "Equipe B",
               "jogadores_a": ["Eli", "Camila"], "jogadores_b": [],
               "eventos_ativos_seq": [2, 3, 5], "equipes_ativas": ["A", "B", "A"]}}
        """.trimIndent())
        val c = Confirmed.fromSnapshot(json)
        assertEquals("p9", c.partidaId)
        assertEquals(3, c.controleVersao)
        assertEquals("relogio-id", c.controleId)
        assertEquals(2 to 1, c.pontosA to c.pontosB)
        assertNull(c.teto)
        assertEquals(listOf("Eli", "Camila"), c.jogadoresA)
        assertEquals(listOf(2 to "A", 3 to "B", 5 to "A"), c.ativos)
        // Sem equipes_ativas coerentes, nada confirmado é desfazível no relógio.
        val semEquipes = JSONObject(json.toString()).apply { getJSONObject("estado_partida").remove("equipes_ativas") }
        assertTrue(Confirmed.fromSnapshot(semEquipes).ativos.isEmpty())
        val off = JSONObject(json.toString()).apply { getJSONObject("quadra").put("controle_id", JSONObject.NULL) }
        assertNull(Confirmed.fromSnapshot(off).controleId)
    }

    @Test
    fun statusShowsPendingCount() {
        assertEquals("● Conectado", statusLine(Connection.CONECTADO, 0))
        assertEquals("Sem conexão · 3 pendentes", statusLine(Connection.SEM_CONEXAO, 3))
    }
}
