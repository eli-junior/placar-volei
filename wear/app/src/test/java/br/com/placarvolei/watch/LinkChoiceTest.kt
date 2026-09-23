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
    @Test fun returnLabelUsesStoredCourt() {
        assertEquals("Retornar à quadra 48291", returnLabel("48291"))
        assertEquals("Retornar à quadra", returnLabel(null))
    }
    @Test fun noWarningWithoutPendingPoints() {
        assertNull(abandonWarning(0, "48291"))
    }
    @Test fun warningCountsAbandonedPoints() {
        assertEquals(
            "3 lances da quadra 48291 ainda não foram enviados. Se o novo código for aprovado, eles serão abandonados.",
            abandonWarning(3, "48291"),
        )
        assertEquals(
            "1 lance da quadra 48291 ainda não foi enviado. Se o novo código for aprovado, ele será abandonado.",
            abandonWarning(1, "48291"),
        )
    }
}
