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
}
