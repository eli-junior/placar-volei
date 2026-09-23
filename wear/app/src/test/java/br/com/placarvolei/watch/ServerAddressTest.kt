package br.com.placarvolei.watch

import org.junit.Assert.assertEquals
import org.junit.Assert.assertThrows
import org.junit.Test

class ServerAddressTest {
    @Test fun blankAddressExplainsMissingField() {
        val error = assertThrows(IllegalArgumentException::class.java) { serverAddress("  ", true) }
        assertEquals("Informe o endereço do placar no campo acima.", error.message)
    }
    @Test fun missingSchemeRequestsHttps() {
        val error = assertThrows(IllegalArgumentException::class.java) { serverAddress("placar.example", true) }
        assertEquals("Use o endereço HTTPS do placar.", error.message)
    }
    @Test fun acceptsHttpsOrigin() { assertEquals("https://placar.example", serverAddress(" https://placar.example/ ", false)) }
    @Test fun rejectsSecretAndPathInServerUrl() {
        for (url in listOf("https://user:secret@placar.example", "https://placar.example/api", "https://placar.example/?secret=x", "https://placar.example/#x")) {
            assertThrows(IllegalArgumentException::class.java) { serverAddress(url, false) }
        }
    }
    @Test fun httpOnlyForDebugBuild() {
        assertThrows(IllegalArgumentException::class.java) { serverAddress("http://10.0.2.2:8000", false) }
        assertEquals("http://10.0.2.2:8000", serverAddress("http://10.0.2.2:8000", true))
    }
}
