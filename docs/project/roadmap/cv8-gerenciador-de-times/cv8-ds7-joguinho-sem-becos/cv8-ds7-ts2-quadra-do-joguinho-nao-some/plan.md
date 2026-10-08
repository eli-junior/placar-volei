# Plano — CV8.DS7.TS2 Quadra do joguinho não some no meio da rodada

Branch: `fix/cv8-ds7-ts2-quadra-do-joguinho` · Versão alvo: **0.46.3** (patch; backend e web, sem mudança de tela nova)

## Como a quadra some hoje

1. **TTL:** `atualizado_em < agora − 3600 s` apaga a quadra (rotina de 5 min e `obter_quadra_sync`); a mesma regra esconde a quadra em `listar_quadras_sync`, derruba comandos (`comandos.py`, 404) e o pareamento do relógio (`watch.py`). Uma rodada parada por mais de 1 h perde a quadra.
2. **Reinício:** `RESET_DB_ON_STARTUP=true` apaga o banco das quadras; o `gerenciador.db` (durável) segue com `sessoes.quadra_id` apontando para o nada.

## Desenho

### 1. A quadra de uma rodada em andamento não expira (batimento)

Em vez de abrir uma exceção em cada um dos ~6 lugares que aplicam o TTL, o servidor **renova `atualizado_em`** das quadras vinculadas a uma rodada `em_andamento`. A regra do TTL fica intacta e uma só função decide quem é protegido.

- `ponte.manter_quadras_da_rodada()`: lê no `gerenciador.db` o `quadra_id` da sessão aberta com rodada `em_andamento` e, se a quadra existe no banco das quadras, faz `UPDATE quadras SET atualizado_em = agora`.
- Roda **uma vez na subida** (depois de `init_db`, antes de qualquer requisição) e **a cada ciclo da rotina de limpeza**, antes de expirar. O ciclo hoje é de 300 s; passa a ser `min(300, TTL/2)` para o batimento sempre vencer o TTL, inclusive nos testes com TTL pequeno.
- Efeitos colaterais aceitos: a quadra protegida sobe na ordem de `/api/quadras` (ordenada por `atualizado_em`) e o pareamento do relógio dela também não vence.
- Rodada `cancelada`/`encerrada` ou sessão encerrada: a quadra volta a expirar normalmente (1 h depois do último batimento).

### 2. Reconciliação do vínculo (quadra inexistente)

`ponte.reconciliar_vinculo(conn)`: se a sessão aberta tem `quadra_id` e essa quadra **não existe mais**:

- **sem partida chamada:** `quadra_id = NULL` (o joguinho deixa de mostrar vínculo com quadra morta; aparece "Nenhuma quadra vinculada" com "Criar quadra e vincular");
- **com partida chamada:** mantém o código — a tela mostra "Quadra 29397 indisponível — anule a partida" (texto que a US16 já entrega) e a saída é **Anular partida**. Depois de anular, o próximo estado limpa o vínculo.

Quando roda: na subida (junto do batimento) e em `estado_sync` (a cada vez que o joguinho monta o estado), numa pequena transação de escrita, só se houver o que mudar. O estado devolvido já reflete a reconciliação.

### Alternativas descartadas

- **Exceção do TTL em cada leitura** (`WHERE ... OR id IN protegidas`): espalha a regra por 6 lugares e acopla `quadras.py` ao `gerenciador.db`.
- **Recriar a quadra com as mesmas duplas** (sugerido no QA F3): o Navigator escolheu a opção (a) — reconciliar e anular. Fica como evolução se a anulação for incômoda.
- **Banco das quadras em volume** (opção b da decisão B): rejeitada pelo Navigator.

## Escopo

- `app/ponte.py`: `manter_quadras_da_rodada`, `reconciliar_vinculo`.
- `app/sessao.py`: `estado_sync` chama a reconciliação.
- `app/main.py`: batimento na subida e na rotina; ciclo `min(300, TTL/2)`.
- Testes de backend (TTL, reinício simulado, partida chamada órfã, anular depois, rodada cancelada volta a expirar).
- Docs: guia de desenvolvimento (seção do banco efêmero), CHANGELOG, roadmap (TS2 → Done após validação), worklog.

## Fora do escopo

- Recriar a quadra automaticamente; mudar `RESET_DB_ON_STARTUP`; US17 (segredo), US18, US19, US20 (mensagens), US21.
- Texto novo na web: as mensagens "indisponível — anule a partida / vincule de novo" já existem. Só reviso se algum e2e depender do vínculo morto.

## Aceite (BDD)

- **Dado** uma rodada em andamento com quadra vinculada **e sem partida chamada** **quando** o servidor reinicia (banco das quadras zerado) **então** o joguinho mostra "Nenhuma quadra vinculada".
- **Dado** o mesmo cenário **com partida chamada** **quando** o servidor reinicia **então** a tela mostra a quadra indisponível e o botão Anular; depois de anular, o vínculo some.
- **Dado** uma rodada em andamento **quando** a quadra fica mais de 1 h sem atualização **então** ela continua existindo, aparece em `/api/quadras` e aceita comandos.
- **Dado** uma rodada cancelada ou sessão encerrada **quando** passa 1 h **então** a quadra expira como antes.

## Riscos

- O batimento muda `atualizado_em` de uma quadra que ninguém tocou. Se o Navigator preferir que "última atividade" reflita só ações reais, a alternativa é a exceção no TTL (descartada acima por custo).
- Cenários 1 e 7 do relatório de furos viram testes de regressão; o teste físico em produção (reiniciar o contêiner no meio de uma rodada) é a validação do Navigator.
