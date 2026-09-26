<script>
  import { onMount } from 'svelte';
  import { fade } from 'svelte/transition';
  import Icone from './Icone.svelte';

  let { onCriarQuadra = () => {}, onEntrarQuadra = () => {}, submetendo = false, erro = null } = $props();

  const CHAVE_APELIDO = 'placar:apelido';
  const CHAVE_TEMA = 'placar:tema';

  let abaAtiva = $state('acompanhar');
  let apelidoCriador = $state('');
  let nomeQuadra = $state('');
  let codigoQuadra = $state('');
  let apelidoEspectador = $state('');
  let temaSol = $state(false);
  let quadrasAtivas = $state([]);
  let carregandoQuadras = $state(false);
  let erroQuadras = $state(false);

  onMount(() => {
    document.body.classList.add('tela-home');
    try {
      const apelidoSalvo = localStorage.getItem(CHAVE_APELIDO);
      if (apelidoSalvo) {
        apelidoCriador = apelidoSalvo;
        apelidoEspectador = apelidoSalvo;
      }
      temaSol = localStorage.getItem(CHAVE_TEMA) === 'sol';
      document.documentElement.toggleAttribute('data-tema', temaSol);
    } catch {}
    carregarQuadrasAtivas();
    return () => document.body.classList.remove('tela-home');
  });

  function alternarTema() {
    temaSol = !temaSol;
    document.documentElement.toggleAttribute('data-tema', temaSol);
    try { localStorage.setItem(CHAVE_TEMA, temaSol ? 'sol' : 'padrao'); } catch {}
  }

  async function carregarQuadrasAtivas() {
    carregandoQuadras = true;
    erroQuadras = false;
    try {
      const resposta = await fetch('/api/quadras');
      if (!resposta.ok) throw new Error('Falha ao consultar quadras');
      const dados = await resposta.json();
      quadrasAtivas = dados.quadras || [];
    } catch {
      erroQuadras = true;
    } finally {
      carregandoQuadras = false;
    }
  }

  function guardarApelido(apelido) {
    try { localStorage.setItem(CHAVE_APELIDO, apelido); } catch {}
  }

  function handleSubmeterCriar(evento) {
    evento.preventDefault();
    const apelido = apelidoCriador.trim();
    if (!apelido) return;
    guardarApelido(apelido);
    onCriarQuadra({ apelido, nome: nomeQuadra.trim() || undefined });
  }

  function handleSubmeterAcompanhar(evento) {
    evento.preventDefault();
    const quadraId = codigoQuadra.trim();
    const apelido = apelidoEspectador.trim();
    if (!quadraId || !apelido) return;
    guardarApelido(apelido);
    onEntrarQuadra({ quadraId, apelido });
  }

  function selecionarQuadraAtiva(quadra) {
    abaAtiva = 'acompanhar';
    codigoQuadra = quadra.id;
    const apelido = apelidoEspectador.trim() || apelidoCriador.trim();
    if (apelido) {
      guardarApelido(apelido);
      onEntrarQuadra({ quadraId: quadra.id, apelido });
      return;
    }
    setTimeout(() => document.getElementById('apelido-espectador')?.focus(), 60);
  }

  function mudarAbaPorTeclado(evento) {
    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(evento.key)) return;
    evento.preventDefault();
    abaAtiva = evento.key === 'ArrowLeft' || evento.key === 'Home' ? 'acompanhar' : 'criar';
    document.getElementById(`aba-${abaAtiva}`)?.focus();
  }
</script>

<main class="home" in:fade={{ duration: 180 }}>
  <nav class="topo" aria-label="Identidade e aparência">
    <a class="marca" href="/" aria-label="Placar Vôlei, início">
      <span class="marca-icone"><Icone nome="bola" tamanho="1.35em" /></span>
      <span>PLACAR <strong>VÔLEI</strong></span>
    </a>
    <button class="tema" type="button" onclick={alternarTema} aria-label={temaSol ? 'Ativar modo escuro' : 'Ativar modo claro'}>
      <Icone nome={temaSol ? 'lua' : 'sol'} tamanho="1.2em" />
      <span>{temaSol ? 'Escuro' : 'Claro'}</span>
    </button>
  </nav>

  <div class="layout">
    <section class="painel-acesso" aria-labelledby="titulo-acesso">
      <div class="abas" role="tablist" aria-label="Como começar">
        <button id="aba-acompanhar" role="tab" type="button" aria-selected={abaAtiva === 'acompanhar'} aria-controls="painel-acompanhar" tabindex={abaAtiva === 'acompanhar' ? 0 : -1} class:ativa={abaAtiva === 'acompanhar'} onclick={() => abaAtiva = 'acompanhar'} onkeydown={mudarAbaPorTeclado}>
          Acompanhar
        </button>
        <button id="aba-criar" role="tab" type="button" aria-selected={abaAtiva === 'criar'} aria-controls="painel-criar" tabindex={abaAtiva === 'criar' ? 0 : -1} class:ativa={abaAtiva === 'criar'} onclick={() => abaAtiva = 'criar'} onkeydown={mudarAbaPorTeclado}>
          Criar placar
        </button>
      </div>

      {#if abaAtiva === 'acompanhar'}
        <form id="painel-acompanhar" aria-labelledby="aba-acompanhar" class="formulario" onsubmit={handleSubmeterAcompanhar}>
          <div class="intro">
            <span class="numero-etapa">01</span>
            <div><h2 id="titulo-acesso">Entre na quadra</h2><p>Use o código exibido no placar.</p></div>
          </div>
          {#if erro}<div class="alerta" role="alert"><Icone nome="alerta" tamanho="1.1em" /><span>{erro}</span></div>{/if}
          <label for="codigo-quadra">Código da quadra</label>
          <input id="codigo-quadra" class="codigo" type="text" inputmode="numeric" pattern="[0-9]*" maxlength="5" autocomplete="one-time-code" bind:value={codigoQuadra} placeholder="00000" required disabled={submetendo} />
          <label for="apelido-espectador">Como vamos chamar você?</label>
          <input id="apelido-espectador" type="text" maxlength="30" autocomplete="nickname" bind:value={apelidoEspectador} placeholder="Seu nome ou apelido" required disabled={submetendo} />
          <button class="acao-principal" type="submit" disabled={submetendo || !codigoQuadra.trim() || !apelidoEspectador.trim()}>
            <span>{submetendo ? 'Entrando…' : 'Acompanhar placar'}</span>
          </button>
        </form>
      {:else}
        <form id="painel-criar" aria-labelledby="aba-criar" class="formulario" onsubmit={handleSubmeterCriar}>
          <div class="intro">
            <span class="numero-etapa">01</span>
            <div><h2 id="titulo-acesso">Abra uma quadra</h2><p>Você começa como administrador do placar.</p></div>
          </div>
          {#if erro}<div class="alerta" role="alert"><Icone nome="alerta" tamanho="1.1em" /><span>{erro}</span></div>{/if}
          <label for="apelido-criador">Como vamos chamar você?</label>
          <input id="apelido-criador" type="text" maxlength="30" autocomplete="nickname" bind:value={apelidoCriador} placeholder="Seu nome ou apelido" required disabled={submetendo} />
          <label for="nome-quadra">Nome da quadra <span>(opcional)</span></label>
          <input id="nome-quadra" type="text" maxlength="50" bind:value={nomeQuadra} placeholder="Ex.: Vôlei de sábado" disabled={submetendo} />
          <button class="acao-principal" type="submit" disabled={submetendo || !apelidoCriador.trim()}>
            <span>{submetendo ? 'Criando…' : 'Criar placar'}</span>
          </button>
        </form>
      {/if}
    </section>

    <section class="ao-vivo" aria-labelledby="titulo-ao-vivo">
      <header class="secao-cabecalho">
        <div><span class="pulso" aria-hidden="true"></span><h2 id="titulo-ao-vivo">Agora na quadra</h2><span class="contagem">{quadrasAtivas.length}</span></div>
        <button type="button" onclick={carregarQuadrasAtivas} disabled={carregandoQuadras} aria-label="Atualizar quadras"><Icone nome="atualizar" tamanho="1.1em" /></button>
      </header>

      {#if carregandoQuadras && quadrasAtivas.length === 0}
        <div class="estado-lista">Procurando partidas…</div>
      {:else if erroQuadras}
        <div class="estado-lista"><p>Não foi possível carregar as quadras.</p><button type="button" onclick={carregarQuadrasAtivas}>Tentar novamente</button></div>
      {:else if quadrasAtivas.length === 0}
        <div class="estado-lista"><p>Nenhuma partida ao vivo agora.</p><button type="button" onclick={() => abaAtiva = 'criar'}>Criar o primeiro placar</button></div>
      {:else}
        <div class="partidas">
          {#each quadrasAtivas as quadra (quadra.id)}
            <button class="partida" type="button" onclick={() => selecionarQuadraAtiva(quadra)} aria-label="Acompanhar {quadra.nome}, código {quadra.id}">
              <div class="partida-info">
                <span class="ao-vivo-badge">AO VIVO</span>
                <h3>{quadra.nome}</h3>
                <span class="codigo-sala">#{quadra.id}</span>
                <span class="participantes"><Icone nome="pessoas" tamanho="1em" /> {quadra.participantes_count || 0}</span>
              </div>
              {#if quadra.partida}
                <div class="placar-resumo">
                  <div class="equipe equipe-a"><span>{quadra.partida.equipe_a}</span><strong>{quadra.partida.pontos_a}</strong></div>
                  <span class="versus">×</span>
                  <div class="equipe equipe-b"><span>{quadra.partida.equipe_b}</span><strong>{quadra.partida.pontos_b}</strong></div>
                </div>
              {:else}
                <div class="aguardando">Aguardando o primeiro saque</div>
              {/if}
              <strong class="partida-abrir">Abrir <Icone nome="seta" tamanho="1em" /></strong>
            </button>
          {/each}
        </div>
      {/if}
    </section>
  </div>
</main>

<style>
  .home { width: min(1180px, 100%); margin: 0 auto; padding: 1.25rem clamp(1rem, 3vw, 2.5rem) 4rem; box-sizing: border-box; color: var(--texto-forte); }
  .topo { display: flex; align-items: center; justify-content: space-between; min-height: 48px; }
  .marca { display: inline-flex; align-items: center; gap: .7rem; color: var(--texto-forte); font-size: .78rem; font-weight: 700; letter-spacing: .18em; text-decoration: none; }
  .marca strong { color: var(--acento-info); }
  .marca-icone { display: grid; place-items: center; width: 36px; height: 36px; border: 1px solid var(--acao-secundaria); border-radius: 10px; }
  .tema { display: inline-flex; align-items: center; justify-content: center; gap: .5rem; min-width: 92px; height: 44px; padding: 0 .85rem; border: 1px solid var(--acao-secundaria); border-radius: 12px; background: var(--fundo-superficie); color: var(--texto-medio); font: inherit; font-size: .78rem; font-weight: 700; cursor: pointer; }
  .secao-cabecalho > button { display: grid; place-items: center; width: 44px; height: 44px; border: 1px solid var(--acao-secundaria); border-radius: 12px; background: var(--fundo-superficie); color: var(--texto-medio); cursor: pointer; }
  .layout { display: grid; grid-template-columns: minmax(320px, .82fr) minmax(420px, 1.18fr); gap: clamp(1rem, 3vw, 2rem); align-items: start; padding-top: clamp(2rem, 6vw, 4.5rem); }
  .painel-acesso, .ao-vivo { min-width: 0; }
  .abas { display: grid; grid-template-columns: 1fr 1fr; padding: 4px; margin-bottom: .75rem; border: 1px solid var(--acao-secundaria); border-radius: 12px; background: var(--fundo-superficie); }
  .abas button { min-height: 44px; border: 0; border-radius: 8px; background: transparent; color: var(--texto-suave); font: inherit; font-size: .86rem; font-weight: 750; cursor: pointer; }
  .abas button.ativa { background: var(--acao-primaria); color: var(--acao-primaria-texto); box-shadow: var(--sombra-sutil); }
  .formulario, .ao-vivo { border: 1px solid var(--acao-secundaria); border-radius: 18px; background: var(--fundo-superficie); box-shadow: var(--sombra-sutil); }
  .formulario { display: flex; flex-direction: column; gap: .65rem; padding: clamp(1.2rem, 3vw, 1.8rem); }
  .intro { display: flex; align-items: flex-start; gap: .9rem; padding-bottom: 1rem; margin-bottom: .15rem; border-bottom: 1px solid var(--acao-secundaria); }
  .numero-etapa { color: var(--acento-info); font-family: var(--fonte-numeros); font-size: 1.5rem; font-weight: 600; line-height: 1; }
  .intro h2 { margin: 0 0 .2rem; font-size: 1.15rem; }
  .intro p { margin: 0; color: var(--texto-suave); font-size: .82rem; }
  label { margin-top: .45rem; color: var(--texto-medio); font-size: .78rem; font-weight: 700; }
  label span { color: var(--texto-apagado); font-weight: 500; }
  input { box-sizing: border-box; width: 100%; min-height: 48px; padding: .75rem .9rem; border: 1px solid var(--acao-secundaria); border-radius: 10px; outline: none; background: var(--fundo-base); color: var(--texto-forte); font: inherit; }
  input:focus { border-color: var(--foco-cor); box-shadow: var(--foco-anel); }
  input.codigo { align-self: center; width: min(100%, 300px); min-height: 64px; padding: .25rem .8rem; font-family: var(--fonte-numeros); font-size: 3.15rem; font-weight: 600; line-height: 1; letter-spacing: .12em; text-align: center; text-indent: .12em; color: var(--acento-info); }
  input.codigo::placeholder { color: var(--texto-apagado); }
  .alerta { display: flex; align-items: flex-start; gap: .6rem; padding: .75rem; border: 1px solid color-mix(in srgb, var(--estado-erro) 45%, transparent); border-radius: 10px; background: color-mix(in srgb, var(--estado-erro) 12%, transparent); color: var(--estado-erro-suave); font-size: .83rem; line-height: 1.4; }
  .acao-principal { display: flex; align-items: center; justify-content: center; min-height: 52px; margin-top: .55rem; padding: 0 1.1rem; border: 0; border-radius: 10px; background: var(--acao-primaria); color: var(--acao-primaria-texto); font: inherit; font-weight: 800; text-align: center; cursor: pointer; }
  .acao-principal:disabled { opacity: .45; cursor: not-allowed; }
  .secao-cabecalho { display: flex; align-items: center; justify-content: space-between; padding: 1rem 1.1rem; border-bottom: 1px solid var(--acao-secundaria); }
  .secao-cabecalho > div { display: flex; align-items: center; gap: .55rem; }
  .secao-cabecalho h2 { margin: 0; font-size: 1rem; }
  .pulso { width: 7px; height: 7px; border-radius: 50%; background: var(--estado-sucesso); box-shadow: 0 0 0 5px color-mix(in srgb, var(--estado-sucesso) 14%, transparent); }
  .contagem { display: grid; place-items: center; min-width: 24px; height: 24px; border-radius: 99px; background: var(--acao-secundaria); color: var(--texto-suave); font-size: .72rem; font-weight: 800; }
  .partidas { display: grid; gap: .75rem; padding: .75rem; }
  .partida { display: grid; grid-template-columns: minmax(110px, .72fr) minmax(250px, 1.55fr) minmax(104px, .68fr); align-items: stretch; width: 100%; min-height: 144px; padding: 0; overflow: hidden; border: 1px solid var(--acao-secundaria); border-top: 3px solid var(--time-a); border-radius: 13px; background: var(--fundo-cartao); color: inherit; text-align: left; cursor: pointer; transition: transform .15s ease, border-color .15s ease; }
  .partida:hover { transform: translateY(-2px); border-color: var(--texto-apagado); }
  .partida-info { display: flex; flex-direction: column; justify-content: center; align-items: flex-start; min-width: 0; padding: .8rem .25rem .8rem .9rem; }
  .partida-info h3 { max-width: 100%; margin: .2rem 0 .4rem; overflow: hidden; color: var(--texto-medio); font-size: .78rem; font-weight: 650; text-overflow: ellipsis; white-space: nowrap; }
  .ao-vivo-badge { color: var(--estado-sucesso); font-size: .61rem; font-weight: 850; letter-spacing: .12em; }
  .codigo-sala { color: var(--texto-suave); font-family: var(--fonte-numeros); font-size: 1.05rem; font-weight: 600; letter-spacing: .05em; }
  .participantes { display: inline-flex; align-items: center; gap: .3rem; margin-top: .45rem; color: var(--texto-suave); font-size: .68rem; }
  .placar-resumo { display: grid; grid-template-columns: minmax(72px, 1fr) 28px minmax(72px, 1fr); align-items: center; justify-items: center; gap: .35rem; min-width: 0; padding: .65rem 1rem; border-inline: 1px solid var(--acao-secundaria); background: linear-gradient(90deg, var(--time-a-tenue), transparent 38%, transparent 62%, var(--time-b-tenue)); }
  .equipe { display: flex; flex-direction: column; align-items: center; min-width: 0; text-align: center; }
  .equipe-b { align-items: center; text-align: center; }
  .equipe span { max-width: 100%; overflow: hidden; color: var(--texto-suave); font-size: .65rem; font-weight: 750; letter-spacing: .08em; text-overflow: ellipsis; text-transform: uppercase; white-space: nowrap; }
  .equipe strong { font-family: var(--fonte-numeros); font-size: clamp(5.5rem, 10vw, 7.4rem); font-weight: 600; line-height: .76; letter-spacing: -.035em; }
  .equipe-a strong { color: var(--time-a); text-shadow: 0 0 24px color-mix(in srgb, var(--time-a) 20%, transparent); }
  .equipe-b strong { color: var(--time-b); text-shadow: 0 0 24px color-mix(in srgb, var(--time-b) 20%, transparent); }
  .versus { color: var(--texto-apagado); font-size: 1.2rem; font-weight: 700; }
  .partida-abrir { align-self: center; display: flex; align-items: center; justify-content: center; gap: .45rem; min-height: 48px; margin: .75rem; padding: 0 .9rem; border-radius: 10px; background: var(--acao-primaria); color: var(--acao-primaria-texto); box-shadow: var(--sombra-sutil); font-size: .82rem; white-space: nowrap; }
  .aguardando, .estado-lista { display: grid; place-items: center; min-height: 145px; padding: 1rem; color: var(--texto-suave); font-size: .85rem; text-align: center; }
  .estado-lista p { margin: 0 0 .8rem; }
  .estado-lista button { min-height: 44px; padding: 0 1rem; border: 1px solid var(--acao-secundaria); border-radius: 9px; background: var(--fundo-cartao); color: var(--texto-medio); font: inherit; font-weight: 700; cursor: pointer; }
  button:focus-visible, a:focus-visible { outline: var(--foco-largura) solid var(--foco-cor); outline-offset: var(--foco-deslocamento); }

  @media (max-width: 800px) {
    .layout { grid-template-columns: 1fr; }
  }
  @media (max-width: 480px) {
    .home { padding: .75rem .8rem 2.5rem; }
    .layout { padding-top: 1.5rem; }
    .formulario { padding: 1rem; }
    .partida { grid-template-columns: minmax(82px, .65fr) minmax(156px, 1.35fr) minmax(72px, .6fr); min-height: 128px; }
    .partida-info { padding-left: .65rem; }
    .placar-resumo { grid-template-columns: minmax(52px, 1fr) 20px minmax(52px, 1fr); padding-inline: .35rem; }
    .equipe strong { font-size: 5rem; }
    .equipe span { max-width: 52px; }
    .partida-abrir { min-height: 44px; margin: .45rem; padding-inline: .5rem; }
  }
  @media (prefers-reduced-motion: reduce) { .partida { transition: none; } }
</style>
