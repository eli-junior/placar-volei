package br.com.placarvolei.watch

import java.net.URI

// O endereço não pode carregar credenciais nem alterar o caminho da API.
fun serverAddress(input: String, debug: Boolean): String {
    val uri = URI(input.trim())
    require(uri.scheme == "https" || (debug && uri.scheme == "http")) {
        "Use o endereço HTTPS do placar."
    }
    require(!uri.host.isNullOrBlank() && uri.rawUserInfo == null && uri.rawQuery == null && uri.rawFragment == null) {
        "Informe somente o endereço do servidor."
    }
    require(uri.path.isNullOrEmpty() || uri.path == "/") { "O endereço não deve conter caminho." }
    return input.trim().trimEnd('/')
}
