<script>
  import { onMount } from 'svelte';
  import Icone from './Icone.svelte';
  import PortaoSegredo from './PortaoSegredo.svelte';
  import { guardarSegredoDono, lerSegredoDono } from '../lib/preferencias.js';
  import { baixarFoto, chamarJogadores, enviarFoto, iniciais, ordenarJogadores, reduzirParaJpeg } from '../lib/jogadores.js';

  let { onVoltar = () => {} } = $props();

  let segredo = $state(lerSegredoDono());
  let jogadores = $state([]);
  let carregando = $state(false);
  let erro = $state(null);
  let erroForm = $state(null);
  let campoErro = $state(null);
  let salvando = $state(false);
  let editandoId = $state(null);
  let nome = $state('');
  let genero = $state('');
  let nota = $state('');
  // Foto: `fotoNova` é o JPEG já reduzido, pendente de envio; `fotoRemover`
  // marca a remoção da foto existente ao salvar. `fotos` guarda as URLs locais
  // das fotos baixadas, por jogador (o <img> não envia o segredo).
  let fotoNova = $state(null);
  let fotoNovaUrl = $state(null);
  let fotoRemover = $state(false);
  let fotos = $state({});
  const versoes = {};

  const ativos = $derived(jogadores.filter(j => j.ativo));
  const inativos = $derived(jogadores.filter(j => !j.ativo));

  onMount(() => {
    if (segredo) carregar();
    return () => {
      for (const url of Object.values(fotos)) URL.revokeObjectURL(url);
      if (fotoNovaUrl) URL.revokeObjectURL(fotoNovaUrl);
    };
  });

  // Baixa só as fotos novas ou trocadas; `versoes` evita refazer a cada recarga.
  async function sincronizarFotos(lista) {
    for (const j of lista) {
      if (!j.tem_foto) {
        if (fotos[j.id]) { URL.revokeObjectURL(fotos[j.id]); delete fotos[j.id]; }
        delete versoes[j.id];
      } else if (!fotos[j.id] || versoes[j.id] === undefined) {
        const url = await baixarFoto(segredo, j.id).catch(() => null);
        if (url) { if (fotos[j.id]) URL.revokeObjectURL(fotos[j.id]); fotos[j.id] = url; versoes[j.id] = true; }
      }
    }
  }

  function esquecerFoto(id) {
    delete versoes[id];
  }

  async function carregar() {
    carregando = true;
    erro = null;
    try {
      const dados = await chamarJogadores(segredo, '?incluir_inativos=true');
      jogadores = ordenarJogadores(dados.jogadores);
      sincronizarFotos(jogadores);
    } catch (e) {
      if (e.status === 404) sair();
      erro = e.message || 'Não foi possível carregar os jogadores.';
    } finally {
      carregando = false;
    }
  }

  async function entrar(digitado) {
    segredo = digitado;
    await carregar();
    if (segredo) guardarSegredoDono(segredo);
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
    nota = '';
    if (fotoNovaUrl) URL.revokeObjectURL(fotoNovaUrl);
    fotoNova = null;
    fotoNovaUrl = null;
    fotoRemover = false;
    erroForm = null;
    campoErro = null;
  }

  function editar(j) {
    editandoId = j.id;
    nome = j.nome;
    genero = j.genero;
    nota = String(j.nota);
    if (fotoNovaUrl) URL.revokeObjectURL(fotoNovaUrl);
    fotoNova = null;
    fotoNovaUrl = null;
    fotoRemover = false;
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
      // type=number: o Svelte entrega null quando o campo está vazio.
      if (nota !== null && nota !== undefined && String(nota).trim() !== '') corpo.nota = Number(nota);
      const salvo = editandoId
        ? await chamarJogadores(segredo, `/${editandoId}`, { metodo: 'PATCH', corpo })
        : await chamarJogadores(segredo, '', { metodo: 'POST', corpo });
      let avisoFoto = null;
      try {
        if (fotoNova) { await enviarFoto(segredo, salvo.id, fotoNova); esquecerFoto(salvo.id); }
        else if (fotoRemover) { await chamarJogadores(segredo, `/${salvo.id}/foto`, { metodo: 'DELETE' }); esquecerFoto(salvo.id); }
      } catch (e) {
        avisoFoto = `Jogador salvo, mas a foto não foi enviada: ${e.message} Abra a edição para tentar de novo.`;
      }
      limparForm();
      await carregar();
      if (avisoFoto) erro = avisoFoto;
    } catch (e) {
      if (e.status === 404 && !editandoId) { sair(); erro = e.message; return; }
      erroForm = e.message;
      campoErro = e.campo || null;
      if (e.campo) setTimeout(() => document.getElementById(`jogador-${e.campo}`)?.focus(), 0);
    } finally {
      salvando = false;
    }
  }

  async function escolherFoto(evento) {
    const arquivo = evento.currentTarget.files?.[0];
    evento.currentTarget.value = '';
    if (!arquivo) return;
    erroForm = null;
    try {
      const jpeg = await reduzirParaJpeg(arquivo);
      if (fotoNovaUrl) URL.revokeObjectURL(fotoNovaUrl);
      fotoNova = jpeg;
      fotoNovaUrl = URL.createObjectURL(jpeg);
      fotoRemover = false;
    } catch (e) {
      erroForm = e.message;
    }
  }

  function removerFoto() {
    if (fotoNovaUrl) URL.revokeObjectURL(fotoNovaUrl);
    fotoNova = null;
    fotoNovaUrl = null;
    fotoRemover = true;
  }

  const fotoAtual = $derived(fotoNovaUrl || (!fotoRemover && editandoId ? fotos[editandoId] : null));

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
    <PortaoSegredo {erro} ocupado={carregando} onEntrar={entrar} />
  {:else}
    <form class="cartao" onsubmit={salvar} aria-labelledby="titulo-form" novalidate>
      <h2 id="titulo-form">{editandoId ? 'Editar jogador' : 'Novo jogador'}</h2>
      {#if erroForm}<div class="alerta" role="alert"><Icone nome="alerta" tamanho="1.1em" /><span>{erroForm}</span></div>{/if}
      <label for="jogador-nome">Nome</label>
      <input id="jogador-nome" type="text" maxlength="40" autocomplete="off" placeholder="Nome e sobrenome" bind:value={nome} aria-invalid={campoErro === 'nome'} disabled={salvando} />
      <fieldset class:erro={campoErro === 'genero'}>
        <legend>Gênero</legend>
        <label class="opcao"><input type="radio" name="jogador-genero" value="H" bind:group={genero} id="jogador-genero" disabled={salvando} /> Homem</label>
        <label class="opcao"><input type="radio" name="jogador-genero" value="M" bind:group={genero} disabled={salvando} /> Mulher</label>
      </fieldset>
      <label for="jogador-nota">Nota <span class="ajuda">(1 a 100; vazio = 60)</span></label>
      <input id="jogador-nota" type="number" inputmode="numeric" min="1" max="100" step="1" placeholder="60" bind:value={nota} aria-invalid={campoErro === 'nota'} disabled={salvando} />
      <div class="foto">
        {#if fotoAtual}<img class="avatar grande" src={fotoAtual} alt="Foto do jogador" />{:else}<span class="avatar grande" aria-hidden="true">{iniciais(nome)}</span>{/if}
        <label class="secundario botao-foto">
          <Icone nome="olho" tamanho="1.1em" /><span>{fotoAtual ? 'Trocar foto' : 'Tirar foto'}</span>
          <input class="oculto" type="file" accept="image/*" capture="environment" onchange={escolherFoto} disabled={salvando} />
        </label>
        {#if fotoAtual}<button class="secundario" type="button" onclick={removerFoto} disabled={salvando}>Remover foto</button>{/if}
      </div>
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
              {#if fotos[j.id]}<img class="avatar" src={fotos[j.id]} alt="" />{:else}<span class="avatar" aria-hidden="true">{iniciais(j.nome)}</span>{/if}
              <span class="nome">{j.nome}</span>
              <span class="genero">{j.genero === 'H' ? 'Homem' : 'Mulher'} · nota {j.nota}</span>
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
              {#if fotos[j.id]}<img class="avatar" src={fotos[j.id]} alt="" />{:else}<span class="avatar" aria-hidden="true">{iniciais(j.nome)}</span>{/if}
              <span class="nome">{j.nome}</span>
              <span class="genero">{j.genero === 'H' ? 'Homem' : 'Mulher'} · nota {j.nota}</span>
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
  label, legend { font-size: var(--texto-apoio); color: var(--texto-medio); }
  input[type='text'], input[type='number'] { box-sizing: border-box; width: 100%; min-height: 48px; padding: .75rem .9rem; border: 1px solid var(--acao-secundaria); border-radius: 10px; outline: none; background: var(--fundo-base); color: var(--texto-forte); font: inherit; }
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
  .ajuda { color: var(--texto-suave); font-size: var(--texto-legenda); }
  .foto { display: flex; flex-wrap: wrap; align-items: center; gap: .6rem; }
  .avatar { display: inline-flex; align-items: center; justify-content: center; flex: none; width: 40px; height: 40px; border-radius: var(--raio-circular); object-fit: cover; background: var(--fundo-cartao-ativo); color: var(--texto-medio); font-size: var(--texto-legenda); font-weight: 800; }
  .avatar.grande { width: 72px; height: 72px; font-size: var(--texto-destaque); }
  .botao-foto { cursor: pointer; }
  .botao-foto:focus-within { outline: 2px solid var(--foco-cor); outline-offset: 2px; }
  .oculto { position: absolute; width: 1px; height: 1px; opacity: 0; overflow: hidden; }
  .vazio { margin: 0; color: var(--texto-suave); }
</style>
