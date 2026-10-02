"""Núcleo do MCP de dispositivos: tudo o que fala com o `adb` e com o build.

Sem dependência do pacote `mcp`, para os testes rodarem com um `adb` falso.
O `servidor.py` só expõe estas funções como ferramentas.

Regras que este módulo aplica para ninguém reaprender na prática:

* celular sempre com `--user 0` (o Samsung duplica o app no perfil Dual App);
* release não atualiza debug (assinatura): recusa e explica, a menos que se
  peça para desinstalar antes (o que apaga os dados do app);
* nunca contorna bloqueio de tela: se o aparelho está bloqueado, pede o
  Navigator;
* porta de pareamento e porta de conexão do `adb` sem fio são diferentes e
  mudam; o mDNS não funciona no WSL, então elas são achadas varrendo a porta.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import socket
import subprocess
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

RAIZ = Path(__file__).resolve().parents[2]
PACOTE = "br.com.placarvolei"
SERVIDOR_PADRAO = "https://placar.elijunior.click"
PORTAS_ADB_SEM_FIO = (30000, 50000)
PNG = b"\x89PNG\r\n\x1a\n"

# Comandos de shell que esta ferramenta nunca roda (o pedido de permissão do
# agente é a barreira principal; isto é só para o que causa dano sem volta).
SHELL_PROIBIDO = (
    r"\breboot\b",
    r"\bsvc\s+power\s+shutdown\b",
    r"\bfactory[_ ]?reset\b",
    r"\bwipe\b",
    r"\brecovery\b",
    r"\brm\s+-[a-z]*r[a-z]*f?\s+/(\s|$)",
    r"\bdd\s+if=",
    r"\bmkfs\b",
    r"\bsu\b",
)


class ErroDispositivo(Exception):
    """Falha esperada, com uma mensagem que diz o que fazer."""


@dataclass
class Resultado:
    codigo: int
    saida: str = ""
    erro: str = ""
    bruto: bytes = b""

    @property
    def ok(self) -> bool:
        return self.codigo == 0

    @property
    def texto(self) -> str:
        return (self.saida + ("\n" + self.erro if self.erro else "")).strip()


Executor = Callable[..., Resultado]


def executar_real(
    args: list[str],
    timeout: float = 60,
    cwd: str | None = None,
    env: dict | None = None,
) -> Resultado:
    try:
        p = subprocess.run(
            args, capture_output=True, timeout=timeout, cwd=cwd, env=env, check=False
        )
    except subprocess.TimeoutExpired:
        return Resultado(
            124, erro=f"tempo esgotado ({timeout:.0f}s): {' '.join(args[:4])}"
        )
    except FileNotFoundError as e:
        return Resultado(127, erro=str(e))
    return Resultado(
        p.returncode,
        p.stdout.decode("utf-8", "replace"),
        p.stderr.decode("utf-8", "replace"),
        p.stdout,
    )


# --- Configuração -----------------------------------------------------------

DISPOSITIVOS_PADRAO = {
    "celular": {"host": "192.168.31.20", "porta": 42637, "tipo": "celular"},
    "relogio": {"host": "192.168.31.235", "porta": 43741, "tipo": "relogio"},
}


def caminho_config() -> Path:
    return Path(
        os.environ.get("PLACAR_DISPOSITIVOS_CONFIG")
        or Path.home() / ".config" / "placar-dispositivos.json"
    )


def ler_config() -> dict:
    """Endereços conhecidos; o arquivo mora fora do repositório (IP é da rede do Navigator)."""
    config = json.loads(json.dumps(DISPOSITIVOS_PADRAO))
    try:
        salvo = json.loads(caminho_config().read_text())
    except (OSError, ValueError):
        return config
    for nome, dados in salvo.items():
        config.setdefault(nome, {}).update(dados)
    return config


def gravar_config(config: dict) -> None:
    caminho = caminho_config()
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(config, indent=2, ensure_ascii=False))


# --- ADB ---------------------------------------------------------------------


def achar_adb() -> str:
    for candidato in (
        os.environ.get("PLACAR_ADB"),
        str(Path.home() / "Android/Sdk/platform-tools/adb"),
        shutil.which("adb"),
    ):
        if candidato and Path(candidato).exists():
            return candidato
    raise ErroDispositivo(
        "adb não encontrado. Instale o Android SDK platform-tools ou defina PLACAR_ADB."
    )


def achar_sdk() -> Path:
    return Path(os.environ.get("ANDROID_HOME") or Path.home() / "Android/Sdk")


def achar_java21() -> str | None:
    if os.environ.get("JAVA_HOME") and "21" in os.environ["JAVA_HOME"]:
        return os.environ["JAVA_HOME"]
    base = Path.home() / ".sdkman/candidates/java"
    candidatos = sorted(base.glob("21*")) if base.exists() else []
    return str(candidatos[-1]) if candidatos else os.environ.get("JAVA_HOME")


def parse_devices(texto: str) -> list[dict]:
    """Saída de `adb devices -l` em lista de {serial, estado, modelo}."""
    aparelhos = []
    for linha in texto.splitlines():
        partes = linha.split()
        if len(partes) < 2 or partes[0] == "List" or partes[0].startswith("*"):
            continue
        modelo = next(
            (p.split(":", 1)[1] for p in partes[2:] if p.startswith("model:")), None
        )
        aparelhos.append({"serial": partes[0], "estado": partes[1], "modelo": modelo})
    return aparelhos


@dataclass
class EstadoTela:
    acordado: bool
    bloqueado: bool
    modo: str

    def descricao(self) -> str:
        if self.bloqueado:
            return f"bloqueado ({self.modo})"
        return (
            "acordado e desbloqueado"
            if self.acordado
            else f"tela apagada ({self.modo})"
        )


def parse_estado_tela(power: str, janela: str) -> EstadoTela:
    modo = (re.search(r"mWakefulness=(\w+)", power) or [None, "?"])[1]
    bloqueado = bool(re.search(r"isKeyguardShowing=true", janela))
    return EstadoTela(acordado=modo == "Awake", bloqueado=bloqueado, modo=modo)


def varrer_portas(
    host: str,
    inicio: int = PORTAS_ADB_SEM_FIO[0],
    fim: int = PORTAS_ADB_SEM_FIO[1],
    tentar: Callable[[str, int], bool] | None = None,
    excluir: tuple[int, ...] = (),
) -> list[int]:
    """Portas TCP abertas no aparelho (as do `adb` sem fio ficam na faixa 30000–50000)."""

    def abre(h: str, p: int) -> bool:
        try:
            with socket.create_connection((h, p), timeout=0.6):
                return True
        except OSError:
            return False

    teste = tentar or abre
    portas = [p for p in range(inicio, fim) if p not in excluir]
    with ThreadPoolExecutor(max_workers=400) as pool:
        achadas = list(pool.map(lambda p: p if teste(host, p) else None, portas))
    return sorted(p for p in achadas if p)


def extrair_png(bruto: bytes) -> bytes:
    """`screencap` em aparelho com duas telas imprime um aviso antes do PNG."""
    inicio = bruto.find(PNG)
    if inicio < 0:
        raise ErroDispositivo(
            "o screencap não devolveu uma imagem (tela apagada ou aparelho bloqueado?)."
        )
    return bruto[inicio:]


def validar_shell(comando: str) -> None:
    for padrao in SHELL_PROIBIDO:
        if re.search(padrao, comando):
            raise ErroDispositivo(
                f"comando recusado por segurança ({padrao}). Peça ao Navigator para rodar à mão."
            )


# --- Dispositivos ------------------------------------------------------------


@dataclass
class Dispositivos:
    """Fala com o `adb`. O executor é injetável para os testes."""

    executor: Executor = executar_real
    adb: str | None = None
    config: dict = field(default_factory=ler_config)

    # base ---------------------------------------------------------------
    def _adb(self) -> str:
        if self.adb is None:
            self.adb = achar_adb()
        return self.adb

    def rodar(self, args: list[str], timeout: float = 60) -> Resultado:
        return self.executor([self._adb(), *args], timeout=timeout)

    def serial(self, dispositivo: str) -> str:
        """Nome conhecido (`celular`, `relogio`) ou um serial literal (`host:porta`)."""
        dados = self.config.get(dispositivo)
        if dados:
            return f"{dados['host']}:{dados['porta']}"
        if re.fullmatch(r"[\w.\-]+(:\d+)?", dispositivo):
            return dispositivo
        raise ErroDispositivo(
            f"dispositivo desconhecido: {dispositivo!r}. Use celular, relogio ou host:porta."
        )

    def tipo(self, dispositivo: str) -> str:
        dados = self.config.get(dispositivo)
        if dados and dados.get("tipo"):
            return dados["tipo"]
        carac = self.shell(dispositivo, "getprop ro.build.characteristics").texto
        return "relogio" if "watch" in carac else "celular"

    def shell(self, dispositivo: str, comando: str, timeout: float = 60) -> Resultado:
        return self.rodar(["-s", self.serial(dispositivo), "shell", comando], timeout)

    def _garantir_conectado(self, dispositivo: str) -> str:
        serial = self.serial(dispositivo)
        if ":" in serial and not self._conectado(serial):
            self.rodar(["connect", serial], timeout=15)
            # O aparelho que acabou de reconectar leva um instante para sair de "offline".
            for _ in range(4):
                if self._conectado(serial):
                    break
                time.sleep(0.75)
            if not self._conectado(serial):
                raise ErroDispositivo(
                    f"{dispositivo} ({serial}) não responde. A porta do adb sem fio muda quando a "
                    "depuração é religada ou a tela dorme: use `conectar` (acha a porta sozinho) ou "
                    "`parear` se o computador ainda não foi pareado."
                )
        return serial

    def _conectado(self, serial: str) -> bool:
        return any(
            d["serial"] == serial and d["estado"] == "device"
            for d in parse_devices(self.rodar(["devices", "-l"]).texto)
        )

    # conexão ------------------------------------------------------------
    def listar(self) -> list[dict]:
        vistos = {
            d["serial"]: d for d in parse_devices(self.rodar(["devices", "-l"]).texto)
        }
        saida = []
        for nome, dados in self.config.items():
            serial = f"{dados['host']}:{dados['porta']}"
            conectado = vistos.pop(serial, None)
            item = {
                "nome": nome,
                "serial": serial,
                "tipo": dados.get("tipo"),
                "conectado": bool(conectado and conectado["estado"] == "device"),
            }
            if conectado and conectado["estado"] == "device":
                item["modelo"] = conectado["modelo"]
                item["tela"] = self.estado_tela(nome).descricao()
            saida.append(item)
        saida += [
            {"nome": None, "serial": s, "estado": d["estado"], "modelo": d["modelo"]}
            for s, d in vistos.items()
        ]
        return saida

    def conectar(self, dispositivo: str, porta: int | None = None) -> str:
        """Conecta ao aparelho. Sem porta, tenta a conhecida e depois varre o aparelho."""
        dados = self.config.get(dispositivo)
        if not dados:
            raise ErroDispositivo(
                f"dispositivo desconhecido: {dispositivo!r}. Use `registrar_dispositivo` primeiro."
            )
        host = dados["host"]
        candidatas = [porta] if porta else [dados["porta"]]
        for p in candidatas:
            if self._tentar_conectar(host, p):
                return self._lembrar(dispositivo, host, p)
        if porta:
            raise ErroDispositivo(
                f"não conectou em {host}:{porta}. Se o computador nunca foi pareado, use `parear`."
            )
        abertas = self.varrer(host, excluir=tuple(candidatas))
        for p in abertas:
            if self._tentar_conectar(host, p):
                return self._lembrar(dispositivo, host, p)
        raise ErroDispositivo(
            f"{dispositivo} ({host}) não aceitou conexão. Portas abertas na faixa do adb sem fio: {abertas or 'nenhuma'}. "
            "Confirme a Depuração por Wi-Fi ligada e a tela do aparelho acesa. Se o computador nunca foi pareado, use `parear`."
        )

    def varrer(self, host: str, excluir: tuple[int, ...] = ()) -> list[int]:
        return varrer_portas(host, excluir=excluir)

    def _tentar_conectar(self, host: str, porta: int) -> bool:
        r = self.rodar(["connect", f"{host}:{porta}"], timeout=20)
        return (
            "connected to" in r.texto
            and "failed" not in r.texto
            and "cannot" not in r.texto
        )

    def _lembrar(self, dispositivo: str, host: str, porta: int) -> str:
        self.config[dispositivo]["porta"] = porta
        gravar_config(self.config)
        return f"conectado em {host}:{porta}"

    def parear(
        self, dispositivo: str, codigo: str, porta_pareamento: int | None = None
    ) -> str:
        """Pareia o computador com o aparelho e conecta. O código vem da tela "Parear novo dispositivo"."""
        dados = self.config.get(dispositivo)
        if not dados:
            raise ErroDispositivo(
                f"dispositivo desconhecido: {dispositivo!r}. Use `registrar_dispositivo` primeiro."
            )
        host = dados["host"]
        candidatas = (
            [porta_pareamento]
            if porta_pareamento
            else self.varrer(host, excluir=(dados["porta"],))
        )
        if not candidatas:
            raise ErroDispositivo(
                f"nenhuma porta aberta em {host}. Na tela do aparelho, abra 'Parear novo dispositivo' e deixe-a visível "
                "(o código e a porta só existem enquanto ela está aberta)."
            )
        pareada = None
        for p in candidatas:
            r = self.executor([self._adb(), "pair", f"{host}:{p}", codigo], timeout=30)
            if "Successfully paired" in r.texto:
                pareada = p
                break
        if pareada is None:
            raise ErroDispositivo(
                "o pareamento falhou: código errado, expirado ou a tela de pareamento foi fechada."
            )
        time.sleep(1)
        # A porta de conexão é outra: varre de novo, sem a de pareamento.
        for p in self.varrer(host, excluir=(pareada,)):
            if self._tentar_conectar(host, p):
                return (
                    f"pareado (porta {pareada}) e {self._lembrar(dispositivo, host, p)}"
                )
        raise ErroDispositivo(
            "pareou, mas não achou a porta de conexão: abra a tela principal da Depuração por Wi-Fi e use `conectar`."
        )

    def registrar(self, nome: str, host: str, porta: int, tipo: str = "celular") -> str:
        self.config[nome] = {"host": host, "porta": porta, "tipo": tipo}
        gravar_config(self.config)
        return f"{nome} = {host}:{porta} ({tipo})"

    def reiniciar_adb(self) -> str:
        self.rodar(["kill-server"], timeout=20)
        self.rodar(["start-server"], timeout=30)
        return "servidor do adb reiniciado; reconecte os aparelhos"

    # estado -------------------------------------------------------------
    def estado_tela(self, dispositivo: str) -> EstadoTela:
        self._garantir_conectado(dispositivo)
        power = self.shell(dispositivo, "dumpsys power").texto
        janela = self.shell(dispositivo, "dumpsys window").texto
        return parse_estado_tela(power, janela)

    def exigir_desbloqueado(self, dispositivo: str) -> None:
        e = self.estado_tela(dispositivo)
        if e.bloqueado or not e.acordado:
            raise ErroDispositivo(
                f"{dispositivo} está {e.descricao()}. Eu não contorno bloqueio de tela: peça ao Navigator para "
                "desbloquear (ou use `tecla WAKEUP` para acordar a tela, se ela só apagou)."
            )

    def info_app(self, dispositivo: str, pacote: str = PACOTE) -> dict:
        self._garantir_conectado(dispositivo)
        pkg = self.shell(dispositivo, f"dumpsys package {pacote}").texto
        versao = (re.search(r"versionName=(\S+)", pkg) or [None, None])[1]
        codigo = (re.search(r"versionCode=(\d+)", pkg) or [None, None])[1]
        usuarios = re.findall(
            r"UserInfo\{(\d+):([^:}]*)", self.shell(dispositivo, "pm list users").texto
        )
        com_app = []
        for uid, nome in usuarios:
            if (
                pacote
                in self.shell(
                    dispositivo, f"pm list packages --user {uid} {pacote}"
                ).texto
            ):
                com_app.append({"usuario": int(uid), "nome": nome})
        return {
            "pacote": pacote,
            "instalado": bool(com_app),
            "versionName": versao,
            "versionCode": codigo and int(codigo),
            "usuarios_com_o_app": com_app,
        }

    # controle ------------------------------------------------------------
    def iniciar_app(
        self, dispositivo: str, pacote: str = PACOTE, atividade: str | None = None
    ) -> str:
        self._garantir_conectado(dispositivo)
        aviso = ""
        e = self.estado_tela(dispositivo)
        if e.bloqueado or not e.acordado:
            aviso = f" Atenção: {dispositivo} está {e.descricao()}; o app abre por trás do bloqueio e só aparece depois de o Navigator desbloquear."
        if atividade:
            r = self.shell(dispositivo, f"am start -W -n {pacote}/{atividade}")
        else:
            r = self.shell(
                dispositivo, f"monkey -p {pacote} -c android.intent.category.LAUNCHER 1"
            )
        if not r.ok or "Error" in r.texto:
            raise ErroDispositivo(f"não abriu {pacote}: {r.texto[-300:]}")
        return f"{pacote} iniciado.{aviso}"

    def parar_app(self, dispositivo: str, pacote: str = PACOTE) -> str:
        self._garantir_conectado(dispositivo)
        self.shell(dispositivo, f"am force-stop {pacote}")
        return f"{pacote} parado"

    def tocar(self, dispositivo: str, x: int, y: int) -> str:
        self.exigir_desbloqueado(dispositivo)
        self.shell(dispositivo, f"input tap {int(x)} {int(y)}")
        return f"toque em ({x}, {y})"

    def deslizar(
        self, dispositivo: str, x1: int, y1: int, x2: int, y2: int, ms: int = 300
    ) -> str:
        self.exigir_desbloqueado(dispositivo)
        self.shell(
            dispositivo,
            f"input swipe {int(x1)} {int(y1)} {int(x2)} {int(y2)} {int(ms)}",
        )
        return f"deslize ({x1},{y1}) → ({x2},{y2})"

    def texto(self, dispositivo: str, texto: str) -> str:
        self.exigir_desbloqueado(dispositivo)
        seguro = re.sub(
            r"[^\w@.\-+]", lambda m: "%s" if m.group() == " " else "", texto
        )
        self.shell(dispositivo, f"input text {seguro}")
        return "texto enviado"

    TECLAS_LIVRES: ClassVar[set[str]] = {
        "KEYCODE_WAKEUP",
        "KEYCODE_SLEEP",
        "KEYCODE_POWER",
    }

    def tecla(self, dispositivo: str, tecla: str) -> str:
        tecla = (
            tecla.upper()
            if tecla.upper().startswith("KEYCODE_")
            else f"KEYCODE_{tecla.upper()}"
        )
        if not re.fullmatch(r"KEYCODE_[A-Z0-9_]+", tecla):
            raise ErroDispositivo(f"tecla inválida: {tecla}")
        if tecla not in self.TECLAS_LIVRES:
            self.exigir_desbloqueado(dispositivo)
        self._garantir_conectado(dispositivo)
        self.shell(dispositivo, f"input keyevent {tecla}")
        return f"{tecla} enviada"

    # observação ---------------------------------------------------------
    def tela_ativa(self, dispositivo: str) -> str | None:
        """Id da tela ativa em aparelho de duas telas (Z Fold); None se só há uma."""
        ids = re.findall(
            r"Display (\d+) \(HWC",
            self.shell(dispositivo, "dumpsys SurfaceFlinger --display-id").texto,
        )
        if len(ids) < 2:
            return None
        displays = self.shell(dispositivo, "dumpsys display").texto
        for achado in re.finditer(
            r"DisplayViewport\{[^}]*isActive=(true|false)[^}]*uniqueId='local:(\d+)'",
            displays,
        ):
            if achado.group(1) == "true":
                return achado.group(2)
        return ids[0]

    def capturar_tela(
        self, dispositivo: str, tela: str | None = None
    ) -> tuple[bytes, str]:
        """PNG da tela e uma nota (estado da tela, qual das duas telas)."""
        serial = self._garantir_conectado(dispositivo)
        estado = self.estado_tela(dispositivo)
        alvo = tela or self.tela_ativa(dispositivo)
        args = ["-s", serial, "exec-out", "screencap", "-p"] + (
            ["-d", alvo] if alvo else []
        )
        r = self.rodar(args, timeout=30)
        nota = f"tela {estado.descricao()}" + (f", display {alvo}" if alvo else "")
        return extrair_png(r.bruto), nota

    def logcat(
        self,
        dispositivo: str,
        filtro: str | None = None,
        linhas: int = 80,
        limpar: bool = False,
    ) -> str:
        self._garantir_conectado(dispositivo)
        if limpar:
            self.rodar(["-s", self.serial(dispositivo), "logcat", "-c"])
            return "logcat limpo"
        texto = self.rodar(
            ["-s", self.serial(dispositivo), "logcat", "-d", "-t", "4000"], timeout=60
        ).texto.splitlines()
        if filtro:
            padrao = re.compile(filtro, re.IGNORECASE)
            texto = [l for l in texto if padrao.search(l)]
        return "\n".join(texto[-max(1, linhas) :])

    def adb_shell(self, dispositivo: str, comando: str, timeout: float = 60) -> str:
        validar_shell(comando)
        self._garantir_conectado(dispositivo)
        return self.shell(dispositivo, comando, timeout).texto

    # build e instalação -------------------------------------------------
    def caminho_apk(self, alvo: str, tipo: str) -> Path:
        if alvo not in ("celular", "relogio") or tipo not in ("debug", "release"):
            raise ErroDispositivo("alvo: celular|relogio; tipo: debug|release")
        base = (
            RAIZ
            / ("android" if alvo == "celular" else "wear")
            / "app/build/outputs/apk"
            / tipo
        )
        return base / f"app-{tipo}.apk"

    def compilar(
        self,
        alvo: str,
        tipo: str = "debug",
        servidor: str | None = None,
        timeout: float = 900,
    ) -> str:
        """Compila o APK. O celular embute o servidor (`PLACAR_SERVIDOR`); release usa a keystore do ~/.gradle/gradle.properties."""
        if tipo == "release" and not _tem_keystore():
            raise ErroDispositivo(
                "release exige placarKeystore* em ~/.gradle/gradle.properties (a keystore fica fora do repositório)."
            )
        env = {**os.environ, "ANDROID_HOME": str(achar_sdk())}
        java = achar_java21()
        if java:
            env["JAVA_HOME"] = java
        if alvo == "celular":
            env["PLACAR_SERVIDOR"] = servidor or SERVIDOR_PADRAO
            args = ["bash", str(RAIZ / "scripts/build-apk.sh"), tipo]
        elif alvo == "relogio":
            tarefa = "assembleRelease" if tipo == "release" else "assembleDebug"
            args = [str(RAIZ / "wear/gradlew"), "-p", str(RAIZ / "wear"), tarefa]
            if servidor:
                args.append(f"-PserverUrl={servidor}")
        else:
            raise ErroDispositivo("alvo: celular|relogio")
        r = self.executor(args, timeout=timeout, cwd=str(RAIZ), env=env)
        apk = self.caminho_apk(alvo, tipo)
        if not r.ok or not apk.exists():
            raise ErroDispositivo(
                f"build falhou (código {r.codigo}):\n{r.texto[-1500:]}"
            )
        return f"{apk} ({apk.stat().st_size // 1024} KB)"

    def instalar(
        self, dispositivo: str, apk: str, desinstalar_antes: bool = False
    ) -> str:
        """Instala o APK. Release não atualiza debug: recusa, a menos que `desinstalar_antes` (apaga os dados do app)."""
        caminho = Path(apk)
        if not caminho.exists():
            raise ErroDispositivo(f"APK não encontrado: {apk}")
        serial = self._garantir_conectado(dispositivo)
        e_celular = self.tipo(dispositivo) == "celular"
        usuario = ["--user", "0"] if e_celular else []
        r = self.rodar(
            ["-s", serial, "install", "-r", *usuario, str(caminho)], timeout=300
        )
        if (
            "INSTALL_FAILED_UPDATE_INCOMPATIBLE" in r.texto
            or "signatures do not match" in r.texto
        ):
            if not desinstalar_antes:
                raise ErroDispositivo(
                    "o app instalado tem assinatura diferente (debug ↔ release). Para trocar é preciso desinstalar o atual, "
                    "o que APAGA os dados do app (quadra local, vínculo). Se o Navigator aceita, repita com desinstalar_antes=true."
                )
            pacote = (
                re.search(r"[Pp]ackage\s+(\S+)\s+signatures", r.texto) or [None, PACOTE]
            )[1]
            self.rodar(["-s", serial, "uninstall", *usuario, pacote], timeout=60)
            r = self.rodar(
                ["-s", serial, "install", *usuario, str(caminho)], timeout=300
            )
        if "Success" not in r.texto:
            raise ErroDispositivo(f"a instalação falhou: {r.texto[-400:]}")
        info = self.info_app(dispositivo)
        extra = ""
        if e_celular and len(info["usuarios_com_o_app"]) > 1:
            extra = f" Atenção: o app também está nos usuários {[u['usuario'] for u in info['usuarios_com_o_app']]} (Dual App)."
        return f"instalado em {dispositivo}: versão {info['versionName']} (code {info['versionCode']}).{extra}"

    def desinstalar(self, dispositivo: str, pacote: str = PACOTE) -> str:
        serial = self._garantir_conectado(dispositivo)
        usuario = ["--user", "0"] if self.tipo(dispositivo) == "celular" else []
        r = self.rodar(["-s", serial, "uninstall", *usuario, pacote], timeout=60)
        return r.texto or "desinstalado"

    def compilar_e_instalar(
        self,
        alvo: str,
        tipo: str = "debug",
        servidor: str | None = None,
        desinstalar_antes: bool = False,
    ) -> str:
        apk = self.compilar(alvo, tipo, servidor)
        return f"compilado: {apk}\n" + self.instalar(
            alvo, apk.split(" (")[0], desinstalar_antes
        )


def _tem_keystore() -> bool:
    try:
        texto = (Path.home() / ".gradle/gradle.properties").read_text()
    except OSError:
        return False
    return all(
        re.search(rf"^{chave}=", texto, re.MULTILINE)
        for chave in (
            "placarKeystore",
            "placarKeystorePassword",
            "placarKeyAlias",
            "placarKeyPassword",
        )
    )
