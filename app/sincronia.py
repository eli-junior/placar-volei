"""Sincronia do gerenciador entre aparelhos (CV8.DS3.US5, CA3).

Hub próprio, separado do das quadras (a rotina de sucessão percorre as salas do
outro e não deve enxergar esta). O estado completo da sessão é publicado a cada
mudança; o cliente que agiu também o recebe na resposta HTTP.
"""

import asyncio
import contextlib
from typing import Any

from app.hub import ConnectionHub

hub_gerenciador = ConnectionHub()
SALA = "gerenciador"


async def publicar(estado: dict[str, Any]) -> None:
    await hub_gerenciador.broadcast(
        SALA, {"tipo": "ESTADO_ATUALIZADO", "payload": estado}
    )


async def publicar_atual() -> None:
    """Recalcula o estado da sessão e o publica (para mudanças fora da sessão,
    como cadastrar ou inativar um jogador)."""
    from app.sessao import estado_sync

    if not await hub_gerenciador.total_conexoes(SALA):
        return
    with contextlib.suppress(Exception):  # sincronia nunca derruba a ação
        await publicar(await asyncio.to_thread(estado_sync))
