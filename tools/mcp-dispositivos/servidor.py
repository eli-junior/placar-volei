# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp>=1.2,<2"]
# ///
"""MCP de dispositivos do Placar Vôlei: o celular e o relógio físicos.

Pareia, conecta, compila, instala, captura a tela, toca e lê o log, com as
armadilhas deste projeto embutidas (ver README.md). Roda por stdio:

    uv run tools/mcp-dispositivos/servidor.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mcp.server.fastmcp import FastMCP, Image
from nucleo import PACOTE, Dispositivos

mcp = FastMCP(
    "dispositivos",
    instructions=(
        "Ferramentas para o celular (Galaxy Z Fold) e o relógio (Galaxy Watch) do Placar Vôlei. Os nomes dos "
        "dispositivos são `celular` e `relogio`. Comece por `listar_dispositivos`. Nunca contorne o bloqueio de tela: "
        "se o aparelho estiver bloqueado, peça ao Navigator para desbloquear. Instalar release sobre debug exige "
        "desinstalar (apaga os dados do app): só com a autorização do Navigator."
    ),
)
_dispositivos = Dispositivos()


async def _em_thread(funcao, *args, **kwargs):
    """O adb e o gradle bloqueiam: rodam fora do laço do servidor."""
    return await asyncio.to_thread(funcao, *args, **kwargs)


# --- conexão -----------------------------------------------------------------


@mcp.tool()
async def listar_dispositivos() -> list[dict]:
    """Aparelhos conhecidos (celular, relogio) e se estão conectados, com o estado da tela de cada um."""
    return await _em_thread(_dispositivos.listar)


@mcp.tool()
async def conectar(dispositivo: str, porta: int | None = None) -> str:
    """Conecta ao celular ou relógio por Wi-Fi. Sem porta, tenta a conhecida e depois varre o aparelho (a porta muda quando a depuração é religada ou a tela dorme)."""
    return await _em_thread(_dispositivos.conectar, dispositivo, porta)


@mcp.tool()
async def parear(
    dispositivo: str, codigo: str, porta_pareamento: int | None = None
) -> str:
    """Pareia o computador com o aparelho e conecta. O código de 6 dígitos vem da tela "Parear novo dispositivo" (a porta de pareamento é achada sozinha; a tela precisa ficar aberta)."""
    return await _em_thread(_dispositivos.parear, dispositivo, codigo, porta_pareamento)


@mcp.tool()
async def descobrir_portas(host: str) -> list[int]:
    """Portas abertas na faixa do adb sem fio (30000–50000) de um IP da rede local."""
    return await _em_thread(_dispositivos.varrer, host)


@mcp.tool()
async def registrar_dispositivo(
    nome: str, host: str, porta: int, tipo: str = "celular"
) -> str:
    """Registra ou atualiza um aparelho (tipo: celular ou relogio). Fica em ~/.config/placar-dispositivos.json, fora do repositório."""
    return await _em_thread(_dispositivos.registrar, nome, host, porta, tipo)


@mcp.tool()
async def reiniciar_adb() -> str:
    """Reinicia o servidor do adb (os aparelhos precisam ser reconectados depois). Use quando o adb travar."""
    return await _em_thread(_dispositivos.reiniciar_adb)


# --- estado ------------------------------------------------------------------


@mcp.tool()
async def estado_tela(dispositivo: str) -> str:
    """Se a tela do aparelho está acordada, apagada ou bloqueada."""
    estado = await _em_thread(_dispositivos.estado_tela, dispositivo)
    return estado.descricao()


@mcp.tool()
async def info_app(dispositivo: str, pacote: str = PACOTE) -> dict:
    """Versão do app instalado e em quais usuários do aparelho ele está (o Samsung pode duplicá-lo no perfil Dual App)."""
    return await _em_thread(_dispositivos.info_app, dispositivo, pacote)


# --- build e instalação --------------------------------------------------------


@mcp.tool()
async def compilar(alvo: str, tipo: str = "debug", servidor: str | None = None) -> str:
    """Compila o APK (alvo: celular ou relogio; tipo: debug ou release). O celular embute o servidor (padrão https://placar.elijunior.click). Release usa a keystore de ~/.gradle/gradle.properties. Leva de 20 s a alguns minutos."""
    return await _em_thread(_dispositivos.compilar, alvo, tipo, servidor)


@mcp.tool()
async def instalar(dispositivo: str, apk: str, desinstalar_antes: bool = False) -> str:
    """Instala um APK no aparelho (celular sempre com --user 0). Se o app instalado tem outra assinatura (debug ↔ release) recusa e explica; desinstalar_antes=true remove o atual e APAGA os dados do app, só com autorização do Navigator."""
    return await _em_thread(_dispositivos.instalar, dispositivo, apk, desinstalar_antes)


@mcp.tool()
async def compilar_e_instalar(
    alvo: str,
    tipo: str = "debug",
    servidor: str | None = None,
    desinstalar_antes: bool = False,
) -> str:
    """Compila o APK do alvo (celular ou relogio) e instala no aparelho correspondente. É o atalho para "gera um APK novo e instala"."""
    return await _em_thread(
        _dispositivos.compilar_e_instalar, alvo, tipo, servidor, desinstalar_antes
    )


@mcp.tool()
async def desinstalar(dispositivo: str, pacote: str = PACOTE) -> str:
    """Desinstala o app (apaga os dados dele). Só com autorização do Navigator."""
    return await _em_thread(_dispositivos.desinstalar, dispositivo, pacote)


# --- controle ------------------------------------------------------------------


@mcp.tool()
async def iniciar_app(
    dispositivo: str, pacote: str = PACOTE, atividade: str | None = None
) -> str:
    """Abre o app. Atividade opcional (ex.: .MainActivity ou br.com.placarvolei.watch.MainActivity). Se a tela está bloqueada, avisa."""
    return await _em_thread(_dispositivos.iniciar_app, dispositivo, pacote, atividade)


@mcp.tool()
async def parar_app(dispositivo: str, pacote: str = PACOTE) -> str:
    """Encerra o processo do app (force-stop)."""
    return await _em_thread(_dispositivos.parar_app, dispositivo, pacote)


@mcp.tool()
async def tocar(dispositivo: str, x: int, y: int) -> str:
    """Toca na tela em pixels (use capturar_tela antes para achar a posição). Recusa se o aparelho estiver bloqueado ou com a tela apagada."""
    return await _em_thread(_dispositivos.tocar, dispositivo, x, y)


@mcp.tool()
async def deslizar(
    dispositivo: str, x1: int, y1: int, x2: int, y2: int, ms: int = 300
) -> str:
    """Desliza o dedo de (x1,y1) a (x2,y2). Recusa se o aparelho estiver bloqueado."""
    return await _em_thread(_dispositivos.deslizar, dispositivo, x1, y1, x2, y2, ms)


@mcp.tool()
async def tecla(dispositivo: str, tecla: str) -> str:
    """Envia uma tecla (HOME, BACK, WAKEUP, SLEEP, ... ou KEYCODE_*). WAKEUP e SLEEP funcionam com a tela apagada; as demais exigem o aparelho desbloqueado. WAKEUP não desbloqueia."""
    return await _em_thread(_dispositivos.tecla, dispositivo, tecla)


@mcp.tool()
async def texto(dispositivo: str, texto: str) -> str:
    """Digita texto no campo em foco (só letras, números e @ . - +; espaços viram espaço)."""
    return await _em_thread(_dispositivos.texto, dispositivo, texto)


# --- observação ------------------------------------------------------------------


@mcp.tool()
async def capturar_tela(dispositivo: str, tela: str | None = None) -> list:
    """Captura a tela como imagem. No Z Fold escolhe sozinho a tela ativa (dobrado ou aberto); `tela` força um display id. Imagem preta costuma ser tela apagada ou bloqueada: a nota diz o estado."""
    png, nota = await _em_thread(_dispositivos.capturar_tela, dispositivo, tela)
    return [nota, Image(data=png, format="png")]


@mcp.tool()
async def logcat(
    dispositivo: str, filtro: str | None = None, linhas: int = 80, limpar: bool = False
) -> str:
    """Últimas linhas do log do aparelho, com filtro opcional (regex, sem diferenciar maiúsculas). limpar=true só limpa o buffer."""
    return await _em_thread(_dispositivos.logcat, dispositivo, filtro, linhas, limpar)


@mcp.tool()
async def adb_shell(dispositivo: str, comando: str, timeout: float = 60) -> str:
    """Comando de shell no aparelho, para o que as outras ferramentas não cobrem. Comandos destrutivos (reboot, wipe, rm -rf /, su...) são recusados."""
    return await _em_thread(_dispositivos.adb_shell, dispositivo, comando, timeout)


if __name__ == "__main__":
    mcp.run()
