"""CV5.DS3.TS1: um socket lento não atrasa a sala."""

import asyncio
import time

import pytest

from app import hub as hub_module
from app.hub import ConnectionHub


class SocketFalso:
    def __init__(self, atraso: float = 0.0):
        self.atraso = atraso
        self.recebidas: list[dict] = []
        self.fechado_com: int | None = None

    async def accept(self):
        pass

    async def send_json(self, message):
        await asyncio.sleep(self.atraso)
        self.recebidas.append(message)

    async def close(self, code=1000):
        self.fechado_com = code


@pytest.mark.asyncio
async def test_socket_lento_nao_atrasa_os_outros(monkeypatch):
    monkeypatch.setattr(hub_module, "ENVIO_TIMEOUT", 0.2)
    hub = ConnectionHub()
    rapido, lento = SocketFalso(), SocketFalso(atraso=10)
    await hub.connect("12345", rapido)
    await hub.connect("12345", lento)

    inicio = time.monotonic()
    await hub.broadcast("12345", {"tipo": "PLACAR_ATUALIZADO"})
    assert time.monotonic() - inicio < 1
    assert rapido.recebidas == [{"tipo": "PLACAR_ATUALIZADO"}]
    assert lento.fechado_com == 1011
    assert await hub.total_conexoes("12345") == 1


@pytest.mark.asyncio
async def test_broadcast_many_mantem_a_ordem():
    hub = ConnectionHub()
    a, b = SocketFalso(), SocketFalso(atraso=0.01)
    await hub.connect("12345", a)
    await hub.connect("12345", b)
    msgs = [{"tipo": "PLACAR_ATUALIZADO"}, {"tipo": "PRESENCA_ATUALIZADA"}]
    await hub.broadcast_many("12345", msgs)
    assert a.recebidas == msgs
    assert b.recebidas == msgs
