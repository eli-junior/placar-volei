<script>
  import { onMount } from 'svelte';
  import Icone from './Icone.svelte';
  import { guardarSegredoDono, lerSegredoDono } from '../lib/preferencias.js';
  import { chamarJogadores, ordenarJogadores } from '../lib/jogadores.js';

  let { onVoltar = () => {} } = $props();

  let segredo = $state(lerSegredoDono());
  let segredoDigitado = $state('');
  let jogadores = $state([]);
  let carregando = $state(false);
  let erro = $state(null);
  let erroForm = $state(null);
  let campoErro = $state(null);
  let salvando = $state(false);
  let editandoId = $state(null);
  let nome = $state('');
  let genero = $state('');

  const ativos = $derived(jogadores.filter(j => j.ativo));
  const inativos = $derived(jogadores.filter(j => !j.ativo));

  onMount(() => { if (segredo) carregar(); });

  async function carregar() {
    carregando = true;
    erro = null;
    try {
      const dados = await chamarJogadores(segredo, '?incluir_inativos=true');
      jogadores = ordenarJogadores(dados.jogadores);
    } catch (e) {
      if (e.status === 404) sair();
      erro = e.message || 'Não foi possível carregar os jogadores.';
    } finally {
      carregando = false;
    }
  }

  async function entrar(evento) {
    evento.preventDefault();
    const digitado = segredoDigitado.trim();
    if (!digitado) return;
    segredo = digitado;
    await carregar();
    if (segredo) guardarSegredoDono(segredo);
    segredoDigitado = '';
  }

  function sair() {
    segredo = '';
    jogadores = [];
    guardarSegredoDono('');
  }

  function limparForm() {
    editandoId = null;
    nome = '';
    genero = '';
    erroForm = null;
    campoErro = null;
  }

  function editar(j) {
    editandoId = j.id;
    nome = j.nome;
    genero = j.genero;
    erroForm = null;
    campoErro = null;
    setTimeout(() => document.getElementById('jogador-nome')?.focus(), 0);
  }

  async function salvar(evento) {
    evento.preventDefault();
    salvando = true;
    erroForm = null;
    campoErro = null;
    try {
      const corpo = { nome, genero };
      if (editandoId) await chamarJogadores(segredo, `/${editandoId}`, { metodo: 'PATCH', corpo });
      else await chamarJogadores(segredo, '', { metodo: 'POST', corpo });
      limparForm();
      await carregar();
    } catch (e) {
      if (e.status === 404 && !editandoId) { sair(); erro = e.message; return; }
      erroForm = e.message;
      campoErro = e.campo || null;
      if (e.campo) setTimeout(() => document.getElementById(`jogador-${e.campo}`)?.focus(), 0);
    } finally {
      salvando = false;
    }
  }

  async function mudarAtivo(j, ativar) {
    erro = null;
    try {
      await chamarJogadores(segredo, `/${j.id}/${ativar ? 'reativar' : 'inativar'}`, { metodo: 'POST' });
      if (editandoId === j.id) limparForm();
      await carregar();
    } catch (e) {
      erro = e.message;
    }
  }
</script>

<main class="jogadores">
  <nav class="topo" aria-label="Navegação">
    <button class="voltar" type="button" onclick={onVoltar}><span aria-hidden="true">←</span><span>Início</span></button>
  </nav>

  <h1>Jogadores</h1>

  {#if !segredo}
    <form class="cartao" onsubmit={entrar}>
      <p>Esta área é protegida. Digite o segredo do dono; ele fica guardado só neste aparelho.</p>
      {#if erro}<div class="alerta" role="alert"><Icone nome="alerta" tamanho="1.1em" /><span>{erro}</span></div>{/if}
      <label for="segredo-dono">Segredo do dono</label>
      <input id="segredo-dono" type="password" autocomplete="off" bind:value={segredoDigitado} required />
      <button class="acao-principal" type="submit" disabled={!segredoDigitado.trim() || carregando}>Entrar</button>
    </form>
  {:else}
    <form class="cartao" onsubmit={salvar} aria-labelledby="titulo-form">
      <h2 id="titulo-form">{editandoId ? 'Editar jogador' : 'Novo jogador'}</h2>
      {#if erroForm}<div class="alerta" role="alert"><Icone nome="alerta" tamanho="1.1em" /><span>{erroForm}</span></div>{/if}
      <label for="jogador-nome">Nome</label>
      <input id="jogador-nome" type="text" maxlength="40" autocomplete="off" bind:value={nome} aria-invalid={campoErro === 'nome'} disabled={salvando} />
      <fieldset class:erro={campoErro === 'genero'}>
        <legend>Gênero</legend>
        <label class="opcao"><input type="radio" name="jogador-genero" value="H" bind:group={genero} id="jogador-genero" disabled={salvando} /> Homem</label>
        <label class="opcao"><input type="radio" name="jogador-genero" value="M" bind:group={genero} disabled={salvando} /> Mulher</label>
      </fieldset>
      <div class="acoes">
        <button class="acao-principal" type="submit" disabled={salvando}>{editandoId ? 'Salvar' : 'Cadastrar'}</button>
        {#if editandoId}<button class="secundario" type="button" onclick={limparForm}>Cancelar</button>{/if}
      </div>
    </form>

    {#if erro}<div class="alerta" role="alert"><Icone nome="alerta" tamanho="1.1em" /><span>{erro}</span></div>{/if}

    <section aria-labelledby="titulo-ativos">
      <h2 id="titulo-ativos">Ativos ({ativos.length})</h2>
      {#if carregando && !jogadores.length}
        <p class="vazio">Carregando…</p>
      {:else if !ativos.length}
        <p class="vazio">Nenhum jogador ativo. Cadastre o primeiro acima.</p>
      {:else}
        <ul class="lista">
          {#each ativos as j (j.id)}
            <li>
              <span class="nome">{j.nome}</span>
              <span class="genero">{j.genero === 'H' ? 'Homem' : 'Mulher'}</span>
              <button class="secundario" type="button" onclick={() => editar(j)} aria-label="Editar {j.nome}">Editar</button>
              <button class="secundario" type="button" onclick={() => mudarAtivo(j, false)} aria-label="Inativar {j.nome}">Inativar</button>
            </li>
          {/each}
        </ul>
      {/if}
    </section>

    {#if inativos.length}
      <section aria-labelledby="titulo-inativos">
        <h2 id="titulo-inativos">Inativos ({inativos.length})</h2>
        <ul class="lista">
          {#each inativos as j (j.id)}
            <li class="inativo">
              <span class="nome">{j.nome}</span>
              <span class="genero">{j.genero === 'H' ? 'Homem' : 'Mulher'}</span>
              <button class="secundario" type="button" onclick={() => mudarAtivo(j, true)} aria-label="Reativar {j.nome}">Reativar</button>
            </li>
          {/each}
        </ul>
      </section>
    {/if}

    <button class="sair" type="button" onclick={sair}>Esquecer segredo neste aparelho</button>
  {/if}
</main>

<style>
  .jogadores { box-sizing: border-box; max-width: 640px; margin: 0 auto; padding: calc(var(--sa-topo) + 1rem) 1rem calc(var(--sa-baixo) + 2rem); display: flex; flex-direction: column; gap: 1rem; color: var(--texto-forte); }
  h1 { margin: 0; font-size: var(--texto-titulo-forte); }
  h2 { margin: 0 0 .5rem; font-size: var(--texto-destaque); }
  .voltar, .secundario, .sair { display: inline-flex; align-items: center; gap: .4rem; min-height: 44px; padding: 0 .85rem; border: 1px solid var(--acao-secundaria); border-radius: 12px; background: var(--fundo-superficie); color: var(--texto-medio); font: inherit; font-size: var(--texto-apoio); font-weight: 700; cursor: pointer; }
  .sair { align-self: flex-start; background: transparent; }
  .cartao { display: flex; flex-direction: column; gap: .6rem; padding: 1rem; border: 1px solid var(--borda-sutil); border-radius: var(--raio-padrao); background: var(--fundo-superficie); }
  .cartao p { margin: 0; color: var(--texto-suave); font-size: var(--texto-apoio); }
  label, legend { font-size: var(--texto-apoio); color: var(--texto-medio); }
  input[type='text'], input[type='password'] { box-sizing: border-box; width: 100%; min-height: 48px; padding: .75rem .9rem; border: 1px solid var(--acao-secundaria); border-radius: 10px; outline: none; background: var(--fundo-base); color: var(--texto-forte); font: inherit; }
  input[aria-invalid='true'] { border-color: var(--estado-erro); }
  input:focus-visible { border-color: var(--foco-cor); box-shadow: var(--foco-anel); }
  fieldset { display: flex; gap: 1.2rem; margin: 0; padding: 0; border: 0; }
  fieldset.erro legend { color: var(--estado-erro-suave); }
  legend { padding: 0; margin-bottom: .3rem; }
  .opcao { display: inline-flex; align-items: center; gap: .5rem; min-height: 44px; }
  .opcao input { width: 1.2rem; height: 1.2rem; }
  .acoes { display: flex; gap: .6rem; }
  .acao-principal { display: flex; align-items: center; justify-content: center; min-height: 52px; padding: 0 1.1rem; border: 0; border-radius: 10px; background: var(--acao-primaria); color: var(--acao-primaria-texto); font: inherit; font-weight: 800; cursor: pointer; }
  .acao-principal:disabled { opacity: .45; cursor: not-allowed; }
  .alerta { display: flex; align-items: flex-start; gap: .6rem; padding: .75rem; border: 1px solid color-mix(in srgb, var(--estado-erro) 45%, transparent); border-radius: 10px; background: color-mix(in srgb, var(--estado-erro) 12%, transparent); color: var(--estado-erro-suave); font-size: .83rem; line-height: 1.4; }
  .lista { display: flex; flex-direction: column; gap: .5rem; margin: 0; padding: 0; list-style: none; }
  li { display: flex; flex-wrap: wrap; align-items: center; gap: .5rem; padding: .6rem .75rem; border: 1px solid var(--borda-sutil); border-radius: var(--raio-padrao); background: var(--fundo-cartao); }
  li.inativo { opacity: .75; }
  .nome { flex: 1 1 8rem; font-weight: 700; }
  .genero { color: var(--texto-suave); font-size: var(--texto-legenda); }
  .vazio { margin: 0; color: var(--texto-suave); }
</style>
