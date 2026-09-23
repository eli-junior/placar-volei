# Plano técnico — CV3.DS1.US1

Checkpoint 1 aprovado pelo Navigator em 2026-09-22. Detalhamento da arquitetura aprovada, sem nova decisão de produto.

## Resultado
Preparar a sala no telefone e vincular um app Wear OS ao participante eli, sem duplicação de presença. Vínculo revogável; autenticação independe do apelido.

## Implementação
- Schema aditivo `watch_grants` / `watch_devices`. Identificador interno `eli-smartwatch`, token aleatório de 32 bytes criado no relógio e guardado via AES-GCM/Android Keystore; banco guarda apenas hash. Código de 8 dígitos, cinco minutos, consumo atômico e limite de tentativas.
- Operador habilita identidade específica por `/api/owner/watch-access`; utilitário de provisionamento pede segredo sem eco. A habilitação é por sala e não integra o segredo de owner ao APK/site.
- Site aprova código e revoga dispositivo. Aprovação requer sessão original e papel ADMIN/CONTROLADOR, além da habilitação explícita pelo operador.
- App consulta estado do vínculo e abre WebSocket autenticado por header. Tokens de dispositivo não funcionam como sessão do navegador para ações administrativas.
- Hub representa telefone e relógio como sockets do mesmo participante, fecha apenas sockets do dispositivo revogado e revalida antes de transmitir eventos ao relógio.
- App usa Kotlin/Compose; configuração inicial de servidor; código e confirmação visual; reconexão enquanto ativo. Vínculo criptografado persiste ao fechar o app. Animação de mudança de estado respeita a escala de animações da plataforma.

## Escopo e versão
Somente vínculo; marcação, desfazer e fila de lances offline ficam nas US2–US4. APK `0.7.0-us1`, sem bump da versão do servidor nem migração destrutiva. Branch `feature/cv3-ds1-us1-vincular-relogio`, a partir de master.

## Riscos conhecidos a validar
Bluetooth com telefone bloqueado, legibilidade circular, teclado para URL (build pode pré-configurá-la), persistência do Keystore no dispositivo real e mudança de presença após suspender o app. A versão inicial é pessoal e a habilitação deve ser refeita em cada sala.

## Evidência e aceite
Ver [roteiro de validação](test-guide.md). A entrega depende do aceite manual do Navigator no Checkpoint 2; build/testes não substituem teste no Galaxy Watch real.
