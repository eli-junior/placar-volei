"""Identidade de rede do cliente, para os limites de tentativa."""

from fastapi import Request
from starlette.websockets import WebSocket

from app.config import settings


def ip_do_cliente(request: Request | WebSocket) -> str:
    """IP real do cliente.

    Atrás do Cloudflare Tunnel, `CF-Connecting-IP` é escrito pelo próprio
    Cloudflare e não pode ser forjado; só vale com `TRUST_CLOUDFLARE` ligado.
    `X-Forwarded-For` nunca é usado: o Cloudflare repassa o valor do cliente.
    """
    if settings.trust_cloudflare:
        ip = request.headers.get("cf-connecting-ip", "").strip()
        if ip:
            return ip
    if request.client and request.client.host:
        return request.client.host
    return "desconhecido"
