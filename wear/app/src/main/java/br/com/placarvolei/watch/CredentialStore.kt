package br.com.placarvolei.watch

import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Base64
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

/**
 * Vínculo guardado no relógio. Desde a CV3.DS1.US5 há dois tokens: o ativo e o
 * do código novo que espera aprovação. O ativo só é trocado quando o servidor
 * confirma o código novo; desistir cancela o pendente e mantém o ativo.
 */
class CredentialStore(context: Context) {
    private val prefs = context.getSharedPreferences("watch-link", Context.MODE_PRIVATE)
    private val alias = "placar-watch-link"

    private fun key(): SecretKey {
        val store = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        (store.getKey(alias, null) as? SecretKey)?.let { return it }
        return KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore").apply {
            init(KeyGenParameterSpec.Builder(alias, KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE).build())
        }.generateKey()
    }

    private fun read(slot: String, ivSlot: String): String? {
        val encrypted = prefs.getString(slot, null) ?: return null
        val iv = Base64.decode(prefs.getString(ivSlot, null), Base64.NO_WRAP)
        return Cipher.getInstance("AES/GCM/NoPadding").run {
            init(Cipher.DECRYPT_MODE, key(), GCMParameterSpec(128, iv))
            String(doFinal(Base64.decode(encrypted, Base64.NO_WRAP)), Charsets.UTF_8)
        }
    }

    private fun encrypt(token: String): Pair<String, String> {
        val cipher = Cipher.getInstance("AES/GCM/NoPadding").apply { init(Cipher.ENCRYPT_MODE, key()) }
        val encrypted = cipher.doFinal(token.toByteArray(Charsets.UTF_8))
        return Base64.encodeToString(encrypted, Base64.NO_WRAP) to Base64.encodeToString(cipher.iv, Base64.NO_WRAP)
    }

    // "token"/"iv" mantêm os nomes da 0.7.0: o vínculo instalado continua valendo.
    fun token(): String? = read("token", "iv")

    fun saveToken(token: String, server: String) {
        val (encrypted, iv) = encrypt(token)
        check(prefs.edit().putString("token", encrypted).putString("iv", iv)
            .putString("server", server).remove("code").remove("court").commit()) { "Não foi possível guardar o vínculo." }
    }
    fun server() = prefs.getString("server", BuildConfig.SERVER_URL).orEmpty()
    fun code() = prefs.getString("code", "").orEmpty()
    fun saveCode(code: String) { check(prefs.edit().putString("code", code).commit()) }

    /** Nome da quadra do vínculo ativo, para "Retornar" mesmo sem rede. */
    fun courtName(): String? = prefs.getString("court", null)
    fun saveCourtName(name: String) { check(prefs.edit().putString("court", name).commit()) }

    /** Token do código novo (US5), guardado antes da rede, como o ativo. */
    fun pendingToken(): String? = read("pending", "pending-iv")
    fun savePendingToken(token: String) {
        val (encrypted, iv) = encrypt(token)
        check(prefs.edit().putString("pending", encrypted).putString("pending-iv", iv)
            .putBoolean("pending-cancel", false).commit()) { "Não foi possível guardar o código novo." }
    }

    /** Desistência ainda não confirmada pelo servidor: refeita ao reconectar. */
    fun cancelPending() = prefs.getBoolean("pending-cancel", false)
    fun markCancelPending() { check(prefs.edit().putBoolean("pending-cancel", true).commit()) }

    fun clearPending() {
        check(prefs.edit().remove("pending").remove("pending-iv").remove("pending-cancel").commit())
    }

    /** Código novo aprovado: ele passa a ser o vínculo ativo, de uma vez. */
    fun promotePending(courtName: String) {
        val encrypted = prefs.getString("pending", null) ?: return
        val iv = prefs.getString("pending-iv", null)
        check(prefs.edit().putString("token", encrypted).putString("iv", iv).putString("court", courtName)
            .remove("pending").remove("pending-iv").remove("pending-cancel").remove("code").commit()) {
            "Não foi possível guardar o vínculo."
        }
    }
}
