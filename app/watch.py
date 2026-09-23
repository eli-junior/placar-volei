"""Vínculo pessoal do Wear OS. Nome de dispositivo nunca concede permissão."""

import asyncio
import re
import secrets
import sqlite3
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field

from app.api import autenticar_owner
from app.comandos import snapshot
from app.config import settings
from app.db import get_db
from app.eventos import get_quadra_lock
from app.hub import hub
from app.identidade import SESSION_COOKIE, hash_sessao
from app.rate_limit import RateLimiter

router = APIRouter(prefix="/api", tags=["relogio"])
creation_limit = RateLimiter(5, 600, 600)
approval_limit = RateLimiter(5, 600, 600)


def now():
    return datetime.now(UTC)


def bearer(headers):
    value = headers.get("authorization", "")
    if not value.startswith("Bearer ") or not re.fullmatch(
        r"[A-Za-z0-9_-]{43}", value[7:]
    ):
        raise HTTPException(401, "Credencial do relógio inválida.")
    return value[7:]


def check_limit(limiter, key):
    blocked, seconds = limiter.esta_bloqueado(key)
    if blocked:
        raise HTTPException(
            429,
            "Muitas tentativas. Aguarde para tentar novamente.",
            headers={"Retry-After": str(seconds)},
        )


def browser_participant(conn, request, court):
    token = request.headers.get("x-session-id") or request.cookies.get(SESSION_COOKIE)
    participant = conn.execute(
        """SELECT p.* FROM participantes p JOIN quadras q ON q.id = p.quadra_id
        WHERE p.quadra_id = ? AND p.session_hash = ? AND q.atualizado_em >= ?""",
        (
            court,
            hash_sessao(token or ""),
            (now() - timedelta(seconds=settings.quadra_ttl_seconds)).isoformat(),
        ),
    ).fetchone()
    if participant is None:
        raise HTTPException(403, "Entre novamente na sala pelo telefone.")
    return participant


def auto_granted(participant):
    names = {n.strip() for n in settings.watch_auto_grant.split(",") if n.strip()}
    return participant["apelido"] in names


def permitted(conn, participant):
    return participant["papel"] in ("ADMIN", "CONTROLADOR") and (
        auto_granted(participant)
        or conn.execute(
            "SELECT 1 FROM watch_grants WHERE participant_id = ?", (participant["id"],)
        ).fetchone()
        is not None
    )


def device_participant(conn, token, court=None):
    participant = conn.execute(
        """SELECT p.id, p.quadra_id, p.apelido, p.papel, d.id AS device_id
        FROM watch_devices d JOIN participantes p ON p.id = d.participant_id
        JOIN watch_grants g ON g.participant_id = p.id
        JOIN quadras q ON q.id = p.quadra_id
        WHERE d.token_hash = ? AND d.revoked = 0 AND d.approved_at IS NOT NULL
        AND p.papel IN ('ADMIN', 'CONTROLADOR') AND q.atualizado_em >= ?""",
        (
            hash_sessao(token),
            (now() - timedelta(seconds=settings.quadra_ttl_seconds)).isoformat(),
        ),
    ).fetchone()
    if participant is None or (court is not None and participant["quadra_id"] != court):
        raise HTTPException(
            401, "Vínculo revogado ou sala indisponível. Use o telefone."
        )
    return dict(participant)


def authenticate_device(token, court=None):
    with get_db() as conn:
        return device_participant(conn, token, court)


def device_active(device_id):
    with get_db() as conn:
        return (
            conn.execute(
                """SELECT 1 FROM watch_devices d
            JOIN participantes p ON p.id = d.participant_id
            JOIN watch_grants g ON g.participant_id = p.id
            JOIN quadras q ON q.id = p.quadra_id
            WHERE d.id = ? AND d.revoked = 0 AND d.approved_at IS NOT NULL
            AND p.papel IN ('ADMIN', 'CONTROLADOR') AND q.atualizado_em >= ?""",
                (
                    device_id,
                    (
                        now() - timedelta(seconds=settings.quadra_ttl_seconds)
                    ).isoformat(),
                ),
            ).fetchone()
            is not None
        )


class GrantBody(BaseModel):
    participant_id: str = Field(min_length=1, max_length=64)
    enabled: bool = True


@router.post("/owner/watch-access")
async def grant_access(body: GrantBody, request: Request):
    # O segredo fica no provisionamento do operador; nunca no site ou APK.
    autenticar_owner(request)

    def update():
        with get_db() as conn:
            conn.execute("BEGIN IMMEDIATE")
            p = conn.execute(
                "SELECT * FROM participantes WHERE id = ?", (body.participant_id,)
            ).fetchone()
            if p is None:
                raise HTTPException(404, "Participante não encontrado.")
            if body.enabled:
                if p["papel"] not in ("ADMIN", "CONTROLADOR") or p["apelido"] != "eli":
                    raise HTTPException(
                        409,
                        "Nesta versão, habilite o participante eli com permissão de controle.",
                    )
                conn.execute(
                    "INSERT OR IGNORE INTO watch_grants VALUES (?)", (p["id"],)
                )
            else:
                conn.execute(
                    "DELETE FROM watch_grants WHERE participant_id = ?", (p["id"],)
                )
                conn.execute(
                    "UPDATE watch_devices SET revoked = 1 WHERE participant_id = ?",
                    (p["id"],),
                )
            return p["quadra_id"]

    court = await asyncio.to_thread(update)
    if not body.enabled:
        await hub.close_watch_connections(court, participant_id=body.participant_id)
    return {"enabled": body.enabled}


@router.post("/watch/pairing", status_code=201)
def start_pairing(request: Request, response: Response):
    token = bearer(request.headers)
    # Não confiar em X-Forwarded-For vindo diretamente do cliente.
    key = request.client.host if request.client else "unknown"
    check_limit(creation_limit, key)
    creation_limit.registrar_falha(key)
    response.headers["Cache-Control"] = "no-store"
    current = now()
    expires = (current + timedelta(minutes=5)).isoformat()
    with get_db() as conn:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute(
            "DELETE FROM watch_devices WHERE participant_id IS NULL AND expires_at < ?",
            (current.isoformat(),),
        )
        previous = conn.execute(
            "SELECT * FROM watch_devices WHERE token_hash = ?", (hash_sessao(token),)
        ).fetchone()
        if previous and previous["participant_id"] is not None:
            raise HTTPException(
                409, "Este dispositivo já foi vinculado. Consulte o estado do vínculo."
            )
        if previous is None and (
            conn.execute(
                "SELECT COUNT(*) FROM watch_devices WHERE participant_id IS NULL"
            ).fetchone()[0]
            >= 20
        ):
            raise HTTPException(
                429,
                "Muitos vínculos pendentes. Tente em cinco minutos.",
                headers={"Retry-After": "300"},
            )
        if previous:
            conn.execute("DELETE FROM watch_devices WHERE id = ?", (previous["id"],))
        # Colisão extremamente improvável, mas tratada sem sobrescrever vínculo alheio.
        for _ in range(10):
            code = f"{secrets.randbelow(100_000_000):08d}"
            try:
                conn.execute(
                    "INSERT INTO watch_devices (id, token_hash, code_hash, expires_at, created_at) VALUES (?, ?, ?, ?, ?)",
                    (
                        str(uuid.uuid4()),
                        hash_sessao(token),
                        hash_sessao(code),
                        expires,
                        current.isoformat(),
                    ),
                )
                break
            except sqlite3.IntegrityError:
                continue
        else:
            raise HTTPException(
                503, "Não foi possível gerar o código. Tente novamente."
            )
    return {"code": code, "expires_at": expires}


@router.get("/watch/session")
def pairing_status(request: Request, response: Response):
    token = bearer(request.headers)
    response.headers["Cache-Control"] = "no-store"
    with get_db() as conn:
        d = conn.execute(
            "SELECT * FROM watch_devices WHERE token_hash = ?", (hash_sessao(token),)
        ).fetchone()
        if d is None:
            raise HTTPException(401, "Vínculo não encontrado. Gere um novo código.")
        if d["participant_id"] is None:
            if d["expires_at"] < now().isoformat():
                raise HTTPException(410, "Código expirado. Gere outro no relógio.")
            return {"status": "pending"}
        p = device_participant(conn, token)
        return {
            "status": "linked",
            "court_id": p["quadra_id"],
            "display_name": p["apelido"],
        }


@router.get("/watch/state")
def watch_state(request: Request, response: Response):
    token = bearer(request.headers)
    response.headers["Cache-Control"] = "no-store"
    with get_db() as conn:
        conn.execute("BEGIN IMMEDIATE")
        p = device_participant(conn, token)
        conn.execute(
            "UPDATE participantes SET ultimo_visto_em = ? WHERE id = ?",
            (now().isoformat(), p["id"]),
        )
        return snapshot(conn, p["quadra_id"])


@router.get("/quadras/{court}/watch")
def list_devices(court: str, request: Request, response: Response):
    response.headers["Cache-Control"] = "no-store"
    with get_db() as conn:
        p = browser_participant(conn, request, court)
        devices = [
            dict(d)
            for d in conn.execute(
                "SELECT id, approved_at FROM watch_devices WHERE participant_id = ? AND revoked = 0",
                (p["id"],),
            )
        ]
        return {"enabled": permitted(conn, p), "devices": devices}


class ApprovalBody(BaseModel):
    code: str = Field(pattern=r"^[0-9]{8}$")


@router.post("/quadras/{court}/watch/approve")
async def approve_device(court: str, body: ApprovalBody, request: Request):
    def approve():
        with get_db() as conn:
            conn.execute("BEGIN IMMEDIATE")
            p = browser_participant(conn, request, court)
            if not permitted(conn, p):
                raise HTTPException(
                    403, "Vínculo de relógio não habilitado para este participante."
                )
            check_limit(approval_limit, p["id"])
            # Habilitação automática vira grant persistido para o relógio autenticar.
            conn.execute("INSERT OR IGNORE INTO watch_grants VALUES (?)", (p["id"],))
            d = conn.execute(
                "SELECT * FROM watch_devices WHERE code_hash = ?",
                (hash_sessao(body.code),),
            ).fetchone()
            if (
                d is None
                or d["participant_id"] is not None
                or d["expires_at"] < now().isoformat()
            ):
                approval_limit.registrar_falha(p["id"])
                raise HTTPException(
                    400, "Código inválido, usado ou expirado. Confira o relógio."
                )
            # Um relógio pessoal por participante. Revínculo não deixa credencial antiga ativa.
            conn.execute(
                "UPDATE watch_devices SET revoked = 1 WHERE participant_id = ?",
                (p["id"],),
            )
            conn.execute(
                "UPDATE watch_devices SET participant_id = ?, approved_at = ?, code_hash = NULL WHERE id = ?",
                (p["id"], now().isoformat(), d["id"]),
            )
            approval_limit.registrar_sucesso(p["id"])
            return p["id"]

    async with get_quadra_lock(court):
        participant = await asyncio.to_thread(approve)
        await hub.close_watch_connections(court, participant_id=participant)
    return {"status": "linked", "display_name": "eli"}


@router.delete("/quadras/{court}/watch/{device_id}")
async def revoke_device(court: str, device_id: str, request: Request):
    def revoke():
        with get_db() as conn:
            conn.execute("BEGIN IMMEDIATE")
            p = browser_participant(conn, request, court)
            result = conn.execute(
                "UPDATE watch_devices SET revoked = 1 WHERE id = ? AND participant_id = ?",
                (device_id, p["id"]),
            )
            if not result.rowcount:
                raise HTTPException(404, "Relógio não encontrado.")

    async with get_quadra_lock(court):
        await asyncio.to_thread(revoke)
        await hub.close_watch_connections(court, device_id=device_id)
    return {"status": "revoked"}
