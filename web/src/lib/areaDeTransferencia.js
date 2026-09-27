/**
 * Copia o texto e diz se deu certo (CV5.DS3.US1). Sem contexto seguro, sem
 * permissão ou sem a API, a promessa é rejeitada: a tela não pode dizer
 * "copiado" nesses casos.
 */
export async function copiarTexto(texto, clipboard = globalThis.navigator?.clipboard) {
  if (!texto || !clipboard?.writeText) return false;
  try {
    await clipboard.writeText(texto);
    return true;
  } catch {
    return false;
  }
}
