package br.com.placarvolei.watch

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class LinkChoiceTest {
    @Test fun linkedWatchOpensOnChoice() {
        assertEquals(Stage.ABERTURA, openingStage(hasLink = true, hasPendingCode = false, cancelling = false))
    }
    @Test fun watchWithoutLinkGoesStraightToPairing() {
        assertEquals(Stage.PLACAR, openingStage(hasLink = false, hasPendingCode = false, cancelling = false))
    }
    @Test fun codeWaitingForApprovalIsShownAgain() {
        assertEquals(Stage.CODIGO_NOVO, openingStage(hasLink = true, hasPendingCode = true, cancelling = false))
    }
    @Test fun giveUpNotYetConfirmedDoesNotTrapTheWatchOnTheCode() {
        assertEquals(Stage.ABERTURA, openingStage(hasLink = true, hasPendingCode = true, cancelling = true))
    }
    @Test fun courtShownByNameOrNumber() {
        assertEquals("q2", courtLabel(" q2 ", "48291"))
        assertEquals("Quadra 48291", courtLabel("", "48291"))
        assertEquals("Voltar para q2", backLabel("q2"))
        assertEquals("Voltar à quadra", backLabel(null))
    }
    @Test fun noWarningWithoutPendingPoints() {
        assertNull(abandonWarning(0, "q2"))
    }
    @Test fun warningCountsAbandonedPoints() {
        assertEquals(
            "3 lances marcados em q2 ainda não foram enviados. Se o novo código for aprovado, eles serão abandonados.",
            abandonWarning(3, "q2"),
        )
        assertEquals(
            "1 lance marcado em q2 ainda não foi enviado. Se o novo código for aprovado, ele será abandonado.",
            abandonWarning(1, "q2"),
        )
    }
}
