"""CV5.DS3.US1: o /ws manda PING para o navegador perceber conexão morta."""

from app import main
from tests.watch_support import prepare


def test_ws_envia_ping_periodico(client, monkeypatch):
    monkeypatch.setattr(main, "PING_INTERVALO", 0)
    court = prepare(client)
    with client.websocket_connect(f"/ws/{court['id']}") as ws:
        assert ws.receive_json()["tipo"] == "ESTADO_INICIAL"
        # Qualquer texto acorda o laço sem esperar os 5 s.
        ws.send_text("oi")
        tipos = set()
        for _ in range(3):
            tipos.add(ws.receive_json()["tipo"])
            if "PING" in tipos:
                break
        assert "PING" in tipos
