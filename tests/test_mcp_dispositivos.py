"""MCP de dispositivos (tools/mcp-dispositivos): lógica com um `adb` falso."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(
    0, str(Path(__file__).resolve().parent.parent / "tools/mcp-dispositivos")
)

import nucleo
from nucleo import Dispositivos, ErroDispositivo, Resultado

PNG = b"\x89PNG\r\n\x1a\n" + b"dados"
POWER_ACORDADO = "  mWakefulness=Awake\n"
POWER_DORMINDO = "  mWakefulness=Dozing\n"
JANELA_LIVRE = "    isKeyguardShowing=false\n"
JANELA_BLOQUEADA = "    isKeyguardShowing=true\n"


class AdbFalso:
    """Responde por prefixo do comando; guarda o que foi chamado."""

    def __init__(self, respostas: dict[str, Resultado | str]):
        self.respostas = respostas
        self.chamadas: list[list[str]] = []

    def __call__(self, args, timeout=60, cwd=None, env=None):
        self.chamadas.append(args[1:] if args[0].endswith("adb") else args)
        comando = " ".join(self.chamadas[-1])
        for prefixo, resposta in self.respostas.items():
            if prefixo in comando:
                if isinstance(resposta, Resultado):
                    return resposta
                return Resultado(0, resposta, bruto=resposta.encode())
        return Resultado(0, "")

    def chamou(self, trecho: str) -> bool:
        return any(trecho in " ".join(c) for c in self.chamadas)


@pytest.fixture(autouse=True)
def config_isolada(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "PLACAR_DISPOSITIVOS_CONFIG", str(tmp_path / "dispositivos.json")
    )


def dispositivos(respostas, **kw) -> tuple[Dispositivos, AdbFalso]:
    adb = AdbFalso(
        {
            "devices -l": "List of devices attached\n192.168.31.20:42637\tdevice product:q6qxxx model:SM_F956B\n192.168.31.235:43741\tdevice model:SM_L330\n",
            **respostas,
        }
    )
    d = Dispositivos(executor=adb, adb="/fake/adb", **kw)
    # Nos testes não há rede para varrer: quem precisa de varredura injeta a sua.
    d.varrer = lambda host, excluir=(): []  # type: ignore[method-assign]
    return d, adb


def test_parse_devices_ignora_cabecalho_e_le_o_modelo():
    saida = "List of devices attached\n* daemon started\n192.168.31.20:42637\tdevice product:q6qxxx model:SM_F956B device:q6q\nXYZ\toffline\n"
    assert nucleo.parse_devices(saida) == [
        {"serial": "192.168.31.20:42637", "estado": "device", "modelo": "SM_F956B"},
        {"serial": "XYZ", "estado": "offline", "modelo": None},
    ]


def test_estado_da_tela_distingue_acordado_apagado_e_bloqueado():
    assert (
        nucleo.parse_estado_tela(POWER_ACORDADO, JANELA_LIVRE).descricao()
        == "acordado e desbloqueado"
    )
    assert nucleo.parse_estado_tela(POWER_DORMINDO, JANELA_BLOQUEADA).bloqueado
    assert (
        "tela apagada"
        in nucleo.parse_estado_tela(POWER_DORMINDO, JANELA_LIVRE).descricao()
    )


def test_varrer_portas_devolve_so_as_abertas_ordenadas():
    abertas = {37885, 43741}
    assert nucleo.varrer_portas(
        "1.2.3.4", 37000, 44000, tentar=lambda h, p: p in abertas
    ) == [37885, 43741]
    assert nucleo.varrer_portas(
        "1.2.3.4", 37000, 44000, tentar=lambda h, p: p in abertas, excluir=(43741,)
    ) == [37885]


def test_extrair_png_pula_o_aviso_de_varias_telas():
    aviso = b"[Warning] Multiple displays were found...\n"
    assert nucleo.extrair_png(aviso + PNG) == PNG
    with pytest.raises(ErroDispositivo, match="não devolveu uma imagem"):
        nucleo.extrair_png(b"nada")


@pytest.mark.parametrize(
    "comando",
    [
        "reboot",
        "svc power shutdown",
        "rm -rf /",
        "su -c id",
        "dd if=/dev/zero of=/sdcard/x",
        "cmd recovery",
    ],
)
def test_shell_recusa_o_que_nao_tem_volta(comando):
    with pytest.raises(ErroDispositivo, match="recusado"):
        nucleo.validar_shell(comando)


def test_shell_deixa_passar_comandos_normais():
    nucleo.validar_shell("dumpsys package br.com.placarvolei")
    nucleo.validar_shell("pm list packages --user 0")


def test_config_nasce_com_os_aparelhos_conhecidos_e_guarda_o_que_muda():
    d, _ = dispositivos({})
    assert d.serial("celular") == "192.168.31.20:42637"
    assert d.serial("relogio") == "192.168.31.235:43741"
    d.registrar("tablet", "192.168.31.50", 5555, "celular")
    salvo = json.loads(nucleo.caminho_config().read_text())
    assert salvo["tablet"]["porta"] == 5555
    assert (
        Dispositivos(executor=AdbFalso({}), adb="/x").serial("tablet")
        == "192.168.31.50:5555"
    )
    with pytest.raises(ErroDispositivo, match="desconhecido"):
        d.serial("geladeira; rm")


def test_toque_recusa_aparelho_bloqueado_e_nao_manda_nada():
    d, adb = dispositivos(
        {"dumpsys power": POWER_ACORDADO, "dumpsys window": JANELA_BLOQUEADA}
    )
    with pytest.raises(ErroDispositivo, match="não contorno bloqueio"):
        d.tocar("celular", 10, 20)
    assert not adb.chamou("input tap")


def test_toque_recusa_tela_apagada_e_funciona_desbloqueado():
    d, _ = dispositivos(
        {"dumpsys power": POWER_DORMINDO, "dumpsys window": JANELA_LIVRE}
    )
    with pytest.raises(ErroDispositivo):
        d.tocar("relogio", 1, 2)
    d2, adb2 = dispositivos(
        {"dumpsys power": POWER_ACORDADO, "dumpsys window": JANELA_LIVRE}
    )
    assert "toque" in d2.tocar("relogio", 120, 280)
    assert adb2.chamou("input tap 120 280")


def test_wakeup_e_sleep_passam_com_a_tela_bloqueada_mas_home_nao():
    d, adb = dispositivos(
        {"dumpsys power": POWER_DORMINDO, "dumpsys window": JANELA_BLOQUEADA}
    )
    assert "KEYCODE_WAKEUP" in d.tecla("celular", "wakeup")
    assert adb.chamou("input keyevent KEYCODE_WAKEUP")
    with pytest.raises(ErroDispositivo):
        d.tecla("celular", "HOME")
    with pytest.raises(ErroDispositivo, match="inválida"):
        d.tecla("celular", "HOME; reboot")


def test_instalar_no_celular_usa_user_0_e_avisa_do_dual_app(tmp_path):
    apk = tmp_path / "a.apk"
    apk.write_bytes(b"x")
    d, adb = dispositivos(
        {
            " install ": "Performing Streamed Install\nSuccess\n",
            "dumpsys package": "    versionName=0.29.0\n    versionCode=4 minSdk=24\n",
            "pm list users": "Users:\n\tUserInfo{0:Eli:4c13} running\n\tUserInfo{95:DUAL_APP:20001010} running\n",
            "pm list packages --user": "package:br.com.placarvolei\n",
        }
    )
    msg = d.instalar("celular", str(apk))
    assert adb.chamou("install -r --user 0")
    assert "0.29.0" in msg and "Dual App" in msg


def test_instalar_no_relogio_nao_usa_user(tmp_path):
    apk = tmp_path / "a.apk"
    apk.write_bytes(b"x")
    d, adb = dispositivos(
        {
            " install ": "Success\n",
            "dumpsys package": "    versionName=0.27.0\n    versionCode=15 \n",
            "pm list users": "Users:\n\tUserInfo{0:Owner:c13} running\n",
            "pm list packages --user": "package:br.com.placarvolei\n",
        }
    )
    d.instalar("relogio", str(apk))
    assert not adb.chamou("--user 0 " + str(apk))
    assert adb.chamou("install -r " + str(apk))


INCOMPATIVEL = Resultado(
    1,
    "Failure [INSTALL_FAILED_UPDATE_INCOMPATIBLE: Existing package br.com.placarvolei signatures do not match newer version; ignoring!]",
)


def test_instalar_release_sobre_debug_recusa_e_explica(tmp_path):
    apk = tmp_path / "a.apk"
    apk.write_bytes(b"x")
    d, adb = dispositivos({" install ": INCOMPATIVEL})
    with pytest.raises(ErroDispositivo, match="APAGA os dados"):
        d.instalar("celular", str(apk))
    assert not adb.chamou("uninstall")


def test_instalar_com_desinstalar_antes_remove_o_atual_e_instala(tmp_path):
    apk = tmp_path / "a.apk"
    apk.write_bytes(b"x")
    respostas = iter([INCOMPATIVEL, Resultado(0, "Success")])

    def adb(args, timeout=60, cwd=None, env=None):
        comando = " ".join(args)
        chamadas.append(comando)
        if " install " in comando:
            return next(respostas)
        if "dumpsys package" in comando:
            return Resultado(0, "versionName=0.29.0\nversionCode=4 ")
        if "pm list users" in comando:
            return Resultado(0, "UserInfo{0:Eli:1} running")
        if "devices -l" in comando:
            return Resultado(
                0, "List of devices attached\n192.168.31.20:42637\tdevice\n"
            )
        if "pm list packages --user" in comando:
            return Resultado(0, "package:br.com.placarvolei")
        return Resultado(0, "")

    chamadas: list[str] = []
    d = Dispositivos(executor=adb, adb="/fake/adb")
    d.instalar("celular", str(apk), desinstalar_antes=True)
    assert any("uninstall --user 0 br.com.placarvolei" in c for c in chamadas)
    assert sum(" install " in c for c in chamadas) == 2


def test_conectar_acha_a_porta_nova_quando_a_conhecida_nao_responde():
    def adb(args, timeout=60, cwd=None, env=None):
        comando = " ".join(args)
        if "connect 192.168.31.235:40000" in comando:
            return Resultado(0, "connected to 192.168.31.235:40000")
        if "connect" in comando:
            return Resultado(0, "failed to connect to 192.168.31.235:43741")
        return Resultado(0, "")

    d = Dispositivos(executor=adb, adb="/fake/adb")
    d.varrer = lambda host, excluir=(): [37885, 40000]  # type: ignore[method-assign]
    assert "40000" in d.conectar("relogio")
    assert json.loads(nucleo.caminho_config().read_text())["relogio"]["porta"] == 40000


def test_parear_acha_a_porta_de_pareamento_e_depois_a_de_conexao(monkeypatch):
    chamadas: list[str] = []

    def adb(args, timeout=60, cwd=None, env=None):
        comando = " ".join(args)
        chamadas.append(comando)
        if "pair 192.168.31.235:37885 717233" in comando:
            return Resultado(0, "Successfully paired to 192.168.31.235:37885")
        if "pair" in comando:
            return Resultado(1, "error: protocol fault")
        if "connect 192.168.31.235:43741" in comando:
            return Resultado(0, "connected to 192.168.31.235:43741")
        return Resultado(0, "")

    d = Dispositivos(executor=adb, adb="/fake/adb")
    varridas = iter([[30001, 37885], [43741]])
    d.varrer = lambda host, excluir=(): next(varridas)  # type: ignore[method-assign]
    monkeypatch.setattr(nucleo.time, "sleep", lambda s: None)
    msg = d.parear("relogio", "717233")
    assert "pareado (porta 37885)" in msg and "43741" in msg
    assert any("pair 192.168.31.235:30001" in c for c in chamadas), (
        "tentou a porta errada antes"
    )


def test_parear_sem_porta_aberta_explica_o_que_fazer():
    d, _ = dispositivos({})
    with pytest.raises(ErroDispositivo, match="Parear novo dispositivo"):
        d.parear("relogio", "123456")


def test_parear_com_codigo_errado_falha_sem_conectar():
    d, _ = dispositivos({"pair": Resultado(1, "error: protocol fault")})
    d.varrer = lambda host, excluir=(): [37885]  # type: ignore[method-assign]
    with pytest.raises(ErroDispositivo, match="código errado"):
        d.parear("relogio", "000000")


def test_captura_escolhe_a_tela_ativa_do_fold_e_limpa_o_aviso():
    d, adb = dispositivos(
        {
            "dumpsys power": POWER_ACORDADO,
            "dumpsys window": JANELA_LIVRE,
            "SurfaceFlinger --display-id": "Display 4630946165277524611 (HWC display 0): port=131\nDisplay 4630947194243491972 (HWC display 3): port=132\n",
            "dumpsys display": "DisplayViewport{type=INTERNAL, valid=true, isActive=false, displayId=1, uniqueId='local:4630947194243491972', x}\nDisplayViewport{type=INTERNAL, valid=true, isActive=true, displayId=0, uniqueId='local:4630946165277524611', y}\n",
            "screencap": Resultado(0, bruto=b"[Warning] Multiple displays\n" + PNG),
        }
    )
    png, nota = d.capturar_tela("celular")
    assert png == PNG
    assert adb.chamou("screencap -p -d 4630946165277524611")
    assert "display 4630946165277524611" in nota


def test_captura_de_aparelho_de_uma_tela_nao_passa_display():
    d, adb = dispositivos(
        {
            "dumpsys power": POWER_ACORDADO,
            "dumpsys window": JANELA_LIVRE,
            "SurfaceFlinger --display-id": "Display 1 (HWC display 0)\n",
            "screencap": Resultado(0, bruto=PNG),
        }
    )
    d.capturar_tela("relogio")
    assert not adb.chamou("screencap -p -d")


def test_aparelho_desconectado_explica_como_voltar():
    adb = AdbFalso({"devices -l": "List of devices attached\n"})
    d = Dispositivos(executor=adb, adb="/fake/adb")
    with pytest.raises(ErroDispositivo, match="`conectar`"):
        d.estado_tela("relogio")


def test_logcat_filtra_e_corta_nas_ultimas_linhas():
    log = "\n".join(
        f"I/Tag: linha {i}" if i % 2 else f"E/CelularDebug: erro {i}" for i in range(10)
    )
    d, _ = dispositivos({"logcat -d": log})
    saida = d.logcat("celular", filtro="celulardebug", linhas=2)
    assert saida.splitlines() == ["E/CelularDebug: erro 6", "E/CelularDebug: erro 8"]


def test_caminhos_dos_apks_e_alvos_invalidos():
    d, _ = dispositivos({})
    assert str(d.caminho_apk("celular", "release")).endswith(
        "android/app/build/outputs/apk/release/app-release.apk"
    )
    assert str(d.caminho_apk("relogio", "debug")).endswith(
        "wear/app/build/outputs/apk/debug/app-debug.apk"
    )
    with pytest.raises(ErroDispositivo):
        d.caminho_apk("geladeira", "debug")


def test_release_sem_keystore_nao_nem_comeca(monkeypatch):
    monkeypatch.setattr(nucleo, "_tem_keystore", lambda: False)
    d, adb = dispositivos({})
    with pytest.raises(ErroDispositivo, match="keystore"):
        d.compilar("celular", "release")
    assert adb.chamadas == []


def test_compilar_celular_embute_o_servidor_e_wear_usa_o_gradle(monkeypatch, tmp_path):
    vistos = []

    def executor(args, timeout=60, cwd=None, env=None):
        vistos.append((args, env))
        return Resultado(0, "BUILD SUCCESSFUL")

    d = Dispositivos(executor=executor, adb="/fake/adb")
    monkeypatch.setattr(
        Dispositivos,
        "caminho_apk",
        lambda self, alvo, tipo: tmp_path / f"{alvo}-{tipo}.apk",
    )
    (tmp_path / "celular-debug.apk").write_bytes(b"x" * 2048)
    (tmp_path / "relogio-release.apk").write_bytes(b"y" * 1024)
    monkeypatch.setattr(nucleo, "_tem_keystore", lambda: True)
    assert "2 KB" in d.compilar("celular", "debug")
    args, env = vistos[-1]
    assert args[0] == "bash" and args[-1] == "debug"
    assert (
        env["PLACAR_SERVIDOR"] == "https://placar.elijunior.click"
        and "ANDROID_HOME" in env
    )
    d.compilar("relogio", "release", servidor="https://x.example")
    args, _ = vistos[-1]
    assert "assembleRelease" in args and "-PserverUrl=https://x.example" in args


def test_build_que_falha_mostra_o_fim_do_log(monkeypatch, tmp_path):
    d = Dispositivos(
        executor=lambda *a, **k: Resultado(1, "x" * 3000 + "FIM DO ERRO"),
        adb="/fake/adb",
    )
    monkeypatch.setattr(
        Dispositivos,
        "caminho_apk",
        lambda self, alvo, tipo: tmp_path / "nao-existe.apk",
    )
    with pytest.raises(ErroDispositivo, match="FIM DO ERRO"):
        d.compilar("celular", "debug")


def test_reconexao_automatica_espera_o_aparelho_sair_de_offline(monkeypatch):
    monkeypatch.setattr(nucleo.time, "sleep", lambda s: None)
    estados = iter(
        ["", "offline", "offline", "device"]
    )  # antes do connect, e depois, a cada checagem

    def adb(args, timeout=60, cwd=None, env=None):
        comando = " ".join(args)
        if "devices -l" in comando:
            estado = next(estados, "device")
            return Resultado(
                0,
                "List of devices attached\n"
                + (f"192.168.31.235:43741\t{estado}\n" if estado else ""),
            )
        if "dumpsys power" in comando:
            return Resultado(0, POWER_ACORDADO)
        if "dumpsys window" in comando:
            return Resultado(0, JANELA_LIVRE)
        return Resultado(0, "connected to 192.168.31.235:43741")

    d = Dispositivos(executor=adb, adb="/fake/adb")
    assert d.estado_tela("relogio").acordado
