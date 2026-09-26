package br.com.placarvolei.watch

import org.junit.Assert.assertEquals
import org.junit.Test

class HeartRateTest {
    @Test
    fun mostraOBatimentoLido() = assertEquals("♥ 132", heartLabel(132))

    @Test
    fun semLeituraMostraTracos() = assertEquals("♥ --", heartLabel(null))

    @Test
    fun leituraForaDaFaixaDoSensorMostraTracos() {
        assertEquals("♥ --", heartLabel(0))
        assertEquals("♥ --", heartLabel(300))
    }
}
