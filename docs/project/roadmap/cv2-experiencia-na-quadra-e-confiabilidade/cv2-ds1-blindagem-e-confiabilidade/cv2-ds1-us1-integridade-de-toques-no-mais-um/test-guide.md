---
code: CV2.DS1.US1
kind: test-guide
status: Active
updated: 2026-09-15
---

# Guia de Teste e Validação — CV2.DS1.US1: Nenhum toque no +1 se perde em silêncio

## 1. Verificação Automatizada

```bash
cd web && npm run check && npm test && npm run build && cd ..
uv run pytest
uv run ruff check . && uv run ruff format --check .
```

`npm run check` roda com `--fail-on-warnings`, então qualquer regressão de acessibilidade ou de CSS morto introduzida nos componentes quebra a verificação.

A lógica de fila vive na interface e não tem cobertura unitária automatizada — é o roteiro manual abaixo que faz esse papel, e ele é obrigatório para a story fechar. O que os testes automatizados garantem é que o backend aceita a sequência de comandos que a fila produz (`tests/test_pontos.py`, `tests/test_desfazer.py`) e que o contrato de erro consumido pela interface é estável (`tests/test_blindagem_e_confiabilidade.py`).

## 2. Roteiro de Validação do Navigator (2 clientes + latência)

### Contexto
- **Cliente A**: navegador de mesa, admin no controle do placar (é onde o DevTools é usado).
- **Cliente B**: celular real ou janela anônima, espectador acompanhando o placar.

### Preparação

```bash
cd web && npm run build && cd ..
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

No **Cliente A**, criar o placar. No **Cliente B**, entrar com o código.

### Cenário 1 — Toques rápidos consecutivos com rede ruim

1. No Cliente A: DevTools → **Network** → **Throttling** → `Slow 3G`.
2. Tocar **cinco vezes seguidas** no `+1` da Equipe A, o mais rápido possível, sem esperar o placar subir.
3. **O que observar**:
   - Cada toque acende o flash do card da equipe (retorno imediato, antes de qualquer resposta).
   - O botão fica pulsando com a barra fina na base enquanto o envio acontece.
   - Enquanto houver mais de um toque pendente, aparece `Enviando N toques na fila…` acima do placar.
   - Ao fim, o placar mostra **5 × 0** no Cliente A **e** no Cliente B.
4. Inspecionar o botão no Elements do DevTools durante o envio: o atributo precisa estar `aria-busy="true"`, voltando a `"false"` quando a fila esvazia.

### Cenário 2 — WebSocket derrubado

1. Ainda no Cliente A, DevTools → Network → **Offline** (ou modo avião no celular) por ~30 segundos.
2. **O que observar**:
   - Os botões `+1` ficam apagados e não respondem ao toque.
   - Um aviso com ícone girando aparece acima do placar dizendo que a conexão caiu e que os botões voltam sozinhos.
   - O chip de reconexão aparece também no painel de controle.
   - O indicador do topo muda de "Ao vivo" para "Conectando...".
3. Tentar acionar o botão pelo teclado (Tab até ele e Enter): nada é marcado, e nenhuma ação silenciosa acontece.
4. Voltar a rede.
5. **O que observar**: em poucos segundos os botões voltam a ficar ativos **sem recarregar a página**, e o placar reconcilia com o estado real do servidor.

### Cenário 3 — Acessibilidade e movimento reduzido

1. Ativar `prefers-reduced-motion` no sistema operacional (macOS: Acessibilidade → Exibição → Reduzir movimento; Windows: Efeitos de animação desligados).
2. Repetir o Cenário 1.
3. **O que observar**: nada pisca nem gira, mas o botão em envio continua distinguível por brilho fixo, e os textos de fila e de reconexão continuam legíveis.

### Cenário 4 — Resiliência (contrato do projeto)

1. Com os dois clientes na sala e alguns pontos marcados, reiniciar o processo (`docker compose restart` ou Ctrl+C e subir de novo).
2. **O que observar**: o placar volta idêntico nos dois clientes depois da reconexão automática.

## 3. Critérios de Sucesso

### Condição de aprovação
- Cinco toques rápidos viram cinco pontos, nas duas telas, sem nenhum desaparecer.
- Todo toque tem retorno visual imediato e `aria-busy="true"` durante o envio.
- Com o socket caído, os botões estão visivelmente desabilitados e existe indicação explícita de reconexão.
- A reconexão devolve o controle sozinha, sem recarregar a página.
- Com movimento reduzido, a informação continua legível sem animação.

### Condição de falha
- Qualquer toque que não vire ponto e não produza mensagem de erro (descarte silencioso — é o débito reaparecendo).
- Botão de `+1` clicável com o indicador em "Conectando...".
- Placar do Cliente B divergindo do Cliente A depois de a fila esvaziar.
- Aviso de fila que não some quando os envios terminam (contador preso).
- Página precisando de recarga manual para voltar a aceitar toques depois da reconexão.
