# Project Briefing

Contexto estável do Placar Vôlei. Premissas que não devem ser re-explicadas a cada sessão.

## Purpose

Placar de vôlei compartilhado em tempo real para peladas. Uma pessoa na quadra marca os pontos e todos os presentes acompanham o placar sincronizado no próprio celular, com registro auditável de cada ponto marcado e de cada correção.

O valor central é **confiança no placar**: em pelada, discussão sobre quem está ganhando é frequente e o histórico ponto a ponto resolve a discussão.

Audiência: o grupo de vôlei do Navigator. Escala esperada: dezenas de pessoas, não milhares.

## Current State

Projeto em fase inicial. Regras de negócio do MVP definidas e validadas pelo Navigator (2026-09-13). Ariad configurado. Nenhum código de aplicação escrito.

Trabalho mais importante agora: `CV1.DS1` — núcleo da partida em tempo real.

## Architecture Premises

- **Backend:** Python + FastAPI. WebSocket para propagação de estado.
- **Persistência:** SQLite, arquivo local. Sem servidor de banco.
- **Frontend:** Svelte 5, compilado em build time e servido como estáticos pelo próprio FastAPI. Animação pelo motion nativo do Svelte, sem biblioteca adicional (`adr` de stack do frontend).
- **Deploy:** contêiner no Mini PC do Navigator, exposto à internet por Cloudflare Tunnel. Build multi-estágio: Node compila o frontend, a imagem final é só Python servindo estáticos. Sem dependência de nuvem de terceiros para dados.
- **Fonte da verdade:** log de eventos append-only. O placar é uma projeção do log, nunca um contador mutável (`adr-0001`).
- **Identidade:** apelido preso à sessão do navegador. Sem cadastro, sem senha, sem provedor externo (`adr-0002`).

## Product Premises

- Uso real acontece **em pé, na beira da quadra, com uma mão** — alvos de toque grandes, nenhuma navegação profunda para marcar ponto.
- A interface é parte do valor, não embalagem: transições animadas comunicam o que mudou no placar a quem está a três metros do celular.
- Conexão de celular em quadra é instável. Reconexão precisa ser transparente e o estado precisa se reconciliar sozinho.
- O placar é um **objeto compartilhado**, não a tela privada de um operador: todos veem a mesma coisa ao mesmo tempo, inclusive as correções.
- Erro de marcação é normal e esperado. Corrigir precisa ser tão fácil quanto marcar.
- O MVP atende pelada, não jogo oficial. Regra formal de vôlei indoor (sets, tie-break, saque, troca de lado) está fora do escopo inicial.

## Constraints

- Nenhum dado sai do Mini PC do Navigator. Sem analytics de terceiros, sem CDN obrigatória para funcionar.
- Sem cadastro de usuário, sem coleta de e-mail, telefone ou qualquer dado pessoal além do apelido informado.
- O segredo de owner vive no `.env` e nunca aparece na UI, em resposta de API pública ou em log de aplicação.
- O log de eventos é append-only. Correção de placar gera novo evento; nada é apagado ou reescrito.
- Node existe apenas em desenvolvimento e no `docker build`. A imagem que roda no Mini PC não tem Node nem `node_modules`.

## Operating Notes

Ver `docs/process/development-guide.md` para comandos, validação e política de commits.

## Glossary

- **Quadra** — sala de jogo. Contém configuração, participantes e a partida corrente. Múltiplas quadras coexistem e são escolhidas numa lista na tela inicial.
- **Partida** — um set único, do 0x0 até o encerramento. Ao encerrar, é arquivada e uma nova começa zerada na mesma quadra.
- **Participante** — pessoa presente numa quadra, identificada por apelido + sessão de navegador.
- **Admin** — participante que configura a quadra e gerencia papéis. O primeiro a entrar na quadra assume o papel.
- **Controlador** — participante autorizado a marcar e desfazer pontos.
- **Espectador** — participante que só acompanha. Também precisa se registrar com apelido.
- **Evento** — registro imutável de uma mudança de estado da partida (`PONTO_MARCADO`, `PONTO_DESFEITO`, `REGRA_ALTERADA`, `PARTIDA_ENCERRADA`, `ADMIN_ASSUMIDO`, entre outros).
- **Linha do tempo** — visualização da sequência de eventos da partida, mostrando como o placar foi construído ponto a ponto.
- **Sucessão** — promoção automática do controlador online há mais tempo quando o admin fica offline além do limite.
- **Owner takeover** — assunção da administração de uma quadra pelo operador da instância, mediante código mestre de 4 dígitos.
- **Owner** — operador da instância (Navigator). Papel de infraestrutura, não de participante; autentica-se pelo segredo do `.env`.
