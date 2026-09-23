package br.com.placarvolei.watch

import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder

class CommandQueueTest {
    @get:Rule val folder = TemporaryFolder()

    @Test
    fun queueSurvivesReopenInOrder() {
        val file = folder.root.resolve("fila.json")
        val commands = listOf("A", "A", "B", "A", "B").mapIndexed { i, e -> PendingCommand("id$i", "p1", 2, e) }
        CommandQueue(file).save(QueueState(commands))
        // Nova instância = app reaberto.
        assertEquals(QueueState(commands), CommandQueue(file).load())
    }

    @Test
    fun heldReasonIsPersistedWithCommands() {
        val file = folder.root.resolve("fila.json")
        val state = QueueState(listOf(PendingCommand("x", "p1", 0, "B")), "A partida já está encerrada.")
        CommandQueue(file).save(state)
        assertEquals(state, CommandQueue(file).load())
        CommandQueue(file).save(QueueState())
        assertEquals(QueueState(), CommandQueue(file).load())
    }

    @Test
    fun missingOrCorruptFileStartsEmpty() {
        val file = folder.root.resolve("fila.json")
        assertEquals(QueueState(), CommandQueue(file).load())
        file.writeText("{corrompido")
        assertEquals(QueueState(), CommandQueue(file).load())
    }

    @Test
    fun undoCommandsRoundTripWithTheirTarget() {
        val file = folder.root.resolve("fila.json")
        val state = QueueState(listOf(
            PendingCommand("p", "p1", 2, "A"),
            PendingCommand("u1", "p1", 2, null, ACAO_DESFAZER, alvoComando = "p"),
            PendingCommand("u2", "p1", 2, null, ACAO_DESFAZER, alvoSeq = 7),
        ))
        CommandQueue(file).save(state)
        assertEquals(state, CommandQueue(file).load())
    }

    @Test
    fun queueWrittenBy080IsReadAsPoints() {
        val file = folder.root.resolve("fila.json")
        file.writeText("""{"comandos":[{"id":"a","partida_id":"p1","controle_versao":1,"equipe":"B"}],"retido":null}""")
        assertEquals(QueueState(listOf(PendingCommand("a", "p1", 1, "B", ACAO_PONTO))), CommandQueue(file).load())
    }

    @Test
    fun requestBodyCarriesOnlyTheFieldsOfItsAction() {
        val ponto = PendingCommand("a", "p1", 1, "A").toJson()
        assertEquals(setOf("id", "partida_id", "controle_versao", "acao", "equipe"), ponto.keys().asSequence().toSet())
        val desfazer = PendingCommand("b", "p1", 1, null, ACAO_DESFAZER, alvoSeq = 4).toJson()
        assertEquals(setOf("id", "partida_id", "controle_versao", "acao", "alvo_seq"), desfazer.keys().asSequence().toSet())
        assertEquals(4, desfazer.getInt("alvo_seq"))
    }
}
