"""Relógio pessoal no Wear OS. Nome de dispositivo nunca concede permissão.

Desde a CV3.DS1.US2 (revisão 3) o relógio age como um participante próprio da
sala, "<dono> (Relógio)", que recebe o controle por delegação do admin. O dono
é o participante do telefone que aprovou o código; é a habilitação dele
(`watch_grants`) que mantém o relógio válido.
"""

import asyncio
import re
import secrets
import sqlite3
import uuid
from datetime import UTC, datetime, timedelta
from typing import Literal

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, model_validator

from app.api import autenticar_owner, transmitir_estado
from app.comandos import MSG_ALVO_MUDOU, executar_sync, snapshot
from app.config import settings
from app.db import get_db
from app.eventos import TipoEvento, append_evento_sync, get_quadra_lock
from app.hub import hub
from app.identidade import SESSION_COOKIE, hash_sessao
from app.quadras import apelido_ja_usado
from app.rate_limit import RateLimiter

router = APIRouter(prefix="/api", tags=["relogio"])
creation_limit = RateLimiter(5, 600, 600)
approval_limit = RateLimiter(5, 600, 600)


def now():
    return datetime.now(UTC)


def room_cutoff():
    return (now() - timedelta(seconds=settings.quadra_ttl_seconds)).isoformat()


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
        (court, hash_sessao(token or ""), room_cutoff()),
    ).fetchone()
    if participant is None:
        raise HTTPException(403, "Entre novamente na sala pelo telefone.")
    return participant


def permitted(conn, participant):
    return participant["papel"] in ("ADMIN", "CONTROLADOR") and (
        conn.execute(
            "SELECT 1 FROM watch_grants WHERE participant_id = ?", (participant["id"],)
        ).fetchone()
        is not None
    )


# Relógio válido: aprovado, não revogado, com dono habilitado e com permissão de
# controle, em sala não expirada. O papel do próprio relógio não importa aqui:
# espectador também acompanha; pontuar depende do controle (executar_sync).
_ACTIVE_DEVICE = """
    FROM watch_devices d
    JOIN participantes p ON p.id = d.participant_id
    JOIN participantes o ON o.id = d.owner_id
    JOIN watch_grants g ON g.participant_id = o.id
    JOIN quadras q ON q.id = p.quadra_id
    WHERE d.revoked = 0 AND d.approved_at IS NOT NULL
    AND o.papel IN ('ADMIN', 'CONTROLADOR') AND q.atualizado_em >= ?"""


def device_participant(conn, token, court=None):
    participant = conn.execute(
        "SELECT p.id, p.quadra_id, p.apelido, p.papel, d.id AS device_id, d.owner_id, o.papel AS dono_papel, q.nome"
        + _ACTIVE_DEVICE
        + " AND d.token_hash = ?",
        (room_cutoff(), hash_sessao(token)),
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
                "SELECT 1" + _ACTIVE_DEVICE + " AND d.id = ?",
                (room_cutoff(), device_id),
            ).fetchone()
            is not None
        )


def watch_participant_of(conn, owner_id):
    """Participante "<dono> (Relógio)" já criado para este dono, se houver."""
    row = conn.execute(
        """SELECT p.* FROM watch_devices d JOIN participantes p ON p.id = d.participant_id
        WHERE d.owner_id = ? ORDER BY d.approved_at DESC LIMIT 1""",
        (owner_id,),
    ).fetchone()
    return row


def remove_watch_participant(conn, court, owner_id, reason):
    """Tira o relógio da sala. Se ele estava no controle, o controle volta ao dono.

    Apagar o participante apaga os vínculos (ON DELETE CASCADE); os recibos e
    os eventos ficam, porque o log é append-only.
    """
    watch = watch_participant_of(conn, owner_id)
    if watch is None:
        return None
    court_row = conn.execute(
        "SELECT controle_id FROM quadras WHERE id = ?", (court,)
    ).fetchone()
    if court_row and court_row["controle_id"] == watch["id"]:
        owner = conn.execute(
            "SELECT id, apelido FROM participantes WHERE id = ?", (owner_id,)
        ).fetchone()
        conn.execute(
            "UPDATE quadras SET controle_id = ?, controle_versao = controle_versao + 1 WHERE id = ?",
            (owner_id, court),
        )
        match = conn.execute(
            "SELECT id FROM partidas WHERE quadra_id = ? ORDER BY criado_em DESC LIMIT 1",
            (court,),
        ).fetchone()
        append_evento_sync(
            settings.db_path,
            court,
            match["id"],
            TipoEvento.CONTROLE_DEVOLVIDO,
            {
                "anterior_id": watch["id"],
                "anterior_apelido": watch["apelido"],
                "controle_id": owner_id,
                "apelido": owner["apelido"],
                "motivo": reason,
            },
            owner_id,
            connection=conn,
        )
    conn.execute("DELETE FROM participantes WHERE id = ?", (watch["id"],))
    return watch["id"]


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
                if (
                    p["papel"] not in ("ADMIN", "CONTROLADOR")
                    or p["apelido"].strip().lower() != "eli"
                ):
                    raise HTTPException(
                        409,
                        "Nesta versão, habilite o participante Eli com permissão de controle.",
                    )
                conn.execute(
                    "INSERT OR IGNORE INTO watch_grants VALUES (?)", (p["id"],)
                )
            else:
                conn.execute(
                    "DELETE FROM watch_grants WHERE participant_id = ?", (p["id"],)
                )
                remove_watch_participant(
                    conn, p["quadra_id"], p["id"], "relogio_desabilitado"
                )
            return p["quadra_id"]

    court = await asyncio.to_thread(update)
    if not body.enabled:
        await hub.close_watch_connections(court)
        await transmitir_estado(court)
    return {"enabled": body.enabled}


class PairingBody(BaseModel):
    # Token do vínculo atual (CV3.DS1.US5). Prova que o código novo vem do
    # mesmo relógio; só o hash é consultado, o token não é gravado.
    substitui: str | None = Field(default=None, pattern=r"^[A-Za-z0-9_-]{43}$")


@router.post("/watch/pairing", status_code=201)
def start_pairing(
    request: Request, response: Response, body: PairingBody | None = None
):
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
        replaced = None
        if body is not None and body.substitui and body.substitui != token:
            # Só um vínculo aprovado e vigente é substituível; os demais
            # não mudam nada, e o código novo vale como vínculo do zero.
            row = conn.execute(
                """SELECT id FROM watch_devices WHERE token_hash = ? AND revoked = 0
                AND participant_id IS NOT NULL""",
                (hash_sessao(body.substitui),),
            ).fetchone()
            replaced = row["id"] if row else None
        # Colisão extremamente improvável, mas tratada sem sobrescrever vínculo alheio.
        for _ in range(10):
            code = f"{secrets.randbelow(100_000_000):08d}"
            try:
                conn.execute(
                    """INSERT INTO watch_devices (id, token_hash, code_hash, expires_at,
                    created_at, substitui_id) VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        str(uuid.uuid4()),
                        hash_sessao(token),
                        hash_sessao(code),
                        expires,
                        current.isoformat(),
                        replaced,
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


@router.delete("/watch/pairing", status_code=204)
def cancel_pairing(request: Request):
    """Desiste de um código ainda não aprovado; o vínculo atual continua.

    Sem o cancelamento, o código abandonado poderia ser aprovado nos minutos
    seguintes e derrubar o vínculo que ele substituiria.
    """
    token = bearer(request.headers)
    with get_db() as conn:
        conn.execute("BEGIN IMMEDIATE")
        d = conn.execute(
            "SELECT participant_id FROM watch_devices WHERE token_hash = ?",
            (hash_sessao(token),),
        ).fetchone()
        if d is not None and d["participant_id"] is not None:
            raise HTTPException(409, "Este código já foi aprovado.")
        conn.execute(
            "DELETE FROM watch_devices WHERE token_hash = ? AND participant_id IS NULL",
            (hash_sessao(token),),
        )
    return Response(status_code=204)


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
            # Nome da quadra (CV3.DS1.US5): o relógio mostra "Retornar" com ele.
            "court_name": p["nome"],
            "participant_id": p["id"],
            "display_name": p["apelido"],
            # Nova partida pelo relógio (CV3.DS2.US3): só com dono administrador.
            "pode_nova_partida": p["dono_papel"] == "ADMIN",
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
                "SELECT id, approved_at FROM watch_devices WHERE owner_id = ? AND revoked = 0",
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
            current = now().isoformat()
            # Um vínculo por vez (CV3.DS1.US5): o vínculo que o código substitui
            # cai agora, na aprovação. Em outra quadra, o relógio sai dela pelo
            # mesmo caminho da revogação pelo telefone.
            watch = watch_participant_of(conn, p["id"])
            replaced = None
            if d["substitui_id"]:
                replaced = conn.execute(
                    """SELECT d.id, d.participant_id, d.owner_id, w.quadra_id
                    FROM watch_devices d JOIN participantes w ON w.id = d.participant_id
                    WHERE d.id = ? AND d.revoked = 0""",
                    (d["substitui_id"],),
                ).fetchone()
            if replaced is not None:
                conn.execute(
                    "UPDATE watch_devices SET revoked = 1 WHERE id = ?",
                    (replaced["id"],),
                )
                if watch is None or replaced["participant_id"] != watch["id"]:
                    remove_watch_participant(
                        conn,
                        replaced["quadra_id"],
                        replaced["owner_id"],
                        "relogio_trocou_de_quadra",
                    )
            # Revínculo reaproveita o participante do relógio: papel e controle
            # delegados continuam valendo com o aparelho novo.
            if watch is None:
                name = f"{p['apelido']} (Relógio)"
                if apelido_ja_usado(conn, court, name, None):
                    raise HTTPException(
                        409, f'O apelido "{name}" já está em uso nesta sala.'
                    )
                watch_id = str(uuid.uuid4())
                conn.execute(
                    """INSERT INTO participantes (id, quadra_id, apelido, papel, criado_em,
                    ultimo_visto_em, session_hash) VALUES (?, ?, ?, 'ESPECTADOR', ?, ?, ?)""",
                    # Hash inalcançável por navegador: o relógio só entra por Bearer.
                    (
                        watch_id,
                        court,
                        name,
                        current,
                        current,
                        hash_sessao(f"relogio:{d['id']}"),
                    ),
                )
            else:
                watch_id, name = watch["id"], watch["apelido"]
            # Um relógio por dono. Revínculo não deixa credencial antiga ativa.
            conn.execute(
                "UPDATE watch_devices SET revoked = 1 WHERE owner_id = ?", (p["id"],)
            )
            conn.execute(
                """UPDATE watch_devices SET participant_id = ?, owner_id = ?, approved_at = ?,
                code_hash = NULL WHERE id = ?""",
                (watch_id, p["id"], current, d["id"]),
            )
            approval_limit.registrar_sucesso(p["id"])
            return watch_id, name, replaced and dict(replaced)

    # Só o lock desta quadra: a quadra antiga é alterada na mesma transação,
    # serializada pelo SQLite; pegar os dois locks arriscaria deadlock entre
    # duas trocas cruzadas.
    async with get_quadra_lock(court):
        watch_id, name, replaced = await asyncio.to_thread(approve)
        await hub.close_watch_connections(court, participant_id=watch_id)
        await transmitir_estado(court)
    if replaced and replaced["quadra_id"] != court:
        await hub.close_watch_connections(
            replaced["quadra_id"], device_id=replaced["id"]
        )
        await transmitir_estado(replaced["quadra_id"])
    return {"status": "linked", "display_name": name}


@router.delete("/quadras/{court}/watch/{device_id}")
async def revoke_device(court: str, device_id: str, request: Request):
    def revoke():
        with get_db() as conn:
            conn.execute("BEGIN IMMEDIATE")
            p = browser_participant(conn, request, court)
            result = conn.execute(
                "UPDATE watch_devices SET revoked = 1 WHERE id = ? AND owner_id = ?",
                (device_id, p["id"]),
            )
            if not result.rowcount:
                raise HTTPException(404, "Relógio não encontrado.")
            remove_watch_participant(conn, court, p["id"], "relogio_revogado")

    async with get_quadra_lock(court):
        await asyncio.to_thread(revoke)
        await hub.close_watch_connections(court, device_id=device_id)
        await transmitir_estado(court)
    return {"status": "revoked"}


_UUID = r"^[0-9a-fA-F-]{36}$"


class CommandBody(BaseModel):
    id: str = Field(pattern=_UUID)
    partida_id: str = Field(min_length=1, max_length=64)
    controle_versao: int = Field(ge=0)
    acao: Literal["ponto", "desfazer", "nova_partida"] = "ponto"
    equipe: Literal["A", "B"] | None = None
    # Desfazer (CV3.DS1.US3): o ponto que o relógio viu no topo. Um ponto já
    # confirmado vai pelo seq; um lance ainda na fila, pelo id do comando.
    alvo_seq: int | None = Field(default=None, ge=1)
    alvo_comando: str | None = Field(default=None, pattern=_UUID)

    @model_validator(mode="after")
    def check_shape(self):
        alvos = (self.alvo_seq is not None) + (self.alvo_comando is not None)
        if self.acao == "ponto" and (self.equipe is None or alvos):
            raise ValueError("Ponto leva a equipe e nenhum alvo.")
        if self.acao == "desfazer" and (self.equipe is not None or alvos != 1):
            raise ValueError("Desfazer leva exatamente um alvo e nenhuma equipe.")
        if self.acao == "nova_partida" and (self.equipe is not None or alvos):
            raise ValueError("Nova partida não leva equipe nem alvo.")
        return self

    @property
    def alvo(self):
        if self.alvo_seq is not None:
            return f"seq:{self.alvo_seq}"
        if self.alvo_comando is not None:
            return f"comando:{self.alvo_comando}"
        return None


def receipt(row):
    return {
        "id": row["comando_id"],
        "status": row["status"],
        "detalhe": row["detalhe"],
        "evento_seq": row["evento_seq"],
    }


def target_of(conn, device_id, body: CommandBody):
    """Seq do ponto criado pelo lance-alvo, que precisa ter sido aplicado.

    O envio é em ordem, então o lance-alvo já passou pelo servidor. Se foi
    recusado, ou é de outra partida, não há ponto dele para desfazer.
    """
    target = conn.execute(
        "SELECT * FROM watch_recibos WHERE device_id = ? AND comando_id = ?",
        (device_id, body.alvo_comando),
    ).fetchone()
    if (
        target is None
        or target["acao"] != "ponto"
        or target["status"] != "APLICADO"
        or target["partida_id"] != body.partida_id
    ):
        raise HTTPException(409, MSG_ALVO_MUDOU)
    return target["evento_seq"]


ACOES = {"ponto": "pontos", "desfazer": "desfazer", "nova_partida": "reiniciar"}


def check_new_match(conn, court, p, body: CommandBody):
    """Relógio no controle, na versão vista, de um dono que é admin da quadra."""
    if p["dono_papel"] != "ADMIN":
        raise HTTPException(403, "Só o relógio de um administrador inicia partida.")
    quadra = conn.execute(
        "SELECT controle_id, controle_versao FROM quadras WHERE id = ?", (court,)
    ).fetchone()
    if quadra["controle_id"] != p["id"]:
        raise HTTPException(403, "Outro operador está no controle do placar.")
    if body.controle_versao != quadra["controle_versao"]:
        raise HTTPException(409, "O controle mudou. Aguarde a atualização do placar.")


def apply_command(token, body: CommandBody, ids_online):
    with get_db() as conn:
        conn.execute("BEGIN IMMEDIATE")
        p = device_participant(conn, token)
        court = p["quadra_id"]
        previous = conn.execute(
            "SELECT * FROM watch_recibos WHERE device_id = ? AND comando_id = ?",
            (p["device_id"], body.id),
        ).fetchone()
        if previous is not None:
            # Reenvio: devolve o mesmo resultado, sem reaplicar efeitos.
            if (
                previous["partida_id"],
                previous["controle_versao"],
                previous["acao"],
                previous["equipe"],
                previous["alvo"],
            ) != (
                body.partida_id,
                body.controle_versao,
                body.acao,
                body.equipe,
                body.alvo,
            ):
                raise HTTPException(409, "Este lance já foi usado com outro conteúdo.")
            return 200, receipt(previous), snapshot(conn, court), False
        current = snapshot(conn, court)
        result = None
        try:
            # Lance de uma partida anterior nunca vale para a atual.
            if body.partida_id != current["partida_id"]:
                raise HTTPException(
                    409, "Uma nova partida começou. Este lance não vale para ela."
                )
            alvo_seq = body.alvo_seq
            if body.alvo_comando is not None:
                alvo_seq = target_of(conn, p["device_id"], body)
            # Mesma regra do site: só quem tem o controle, na versão vista, pontua.
            # Nova partida (CV3.DS2.US3): o `reiniciar` do site, nos mesmos
            # moldes, em nome do relógio que está com o controle de um admin.
            if body.acao == "nova_partida":
                check_new_match(conn, court, p, body)
            result = executar_sync(
                settings.db_path,
                court,
                None,
                ACOES[body.acao],
                equipe=body.equipe,
                alvo_seq=alvo_seq,
                versao=str(body.controle_versao),
                ids_online=ids_online,
                autor_id=p["id"],
                connection=conn,
                dono_admin=body.acao == "nova_partida",
            )
            status, detail, seq = "APLICADO", None, result["evento"]["seq"]
            # Vai junto no broadcast: o relógio tira o lance da fila ao ver o
            # snapshot, mesmo que ele chegue antes da resposta HTTP.
            result["comando_id"] = body.id
        except HTTPException as e:
            # As verificações de negócio ocorrem antes de qualquer escrita.
            status, detail, seq = "RECUSADO", e.detail, None
        created = now().isoformat()
        conn.execute(
            """INSERT INTO watch_recibos (device_id, comando_id, quadra_id, partida_id,
            acao, equipe, alvo, controle_versao, status, detalhe, evento_seq, criado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                p["device_id"],
                body.id,
                court,
                body.partida_id,
                body.acao,
                body.equipe,
                body.alvo,
                body.controle_versao,
                status,
                detail,
                seq,
                created,
            ),
        )
        conn.execute(
            "UPDATE participantes SET ultimo_visto_em = ? WHERE id = ?",
            (created, p["id"]),
        )
        rec = {"id": body.id, "status": status, "detalhe": detail, "evento_seq": seq}
        applied = result is not None
        return (201 if applied else 200), rec, result or current, applied


@router.post("/watch/comandos")
async def watch_command(body: CommandBody, request: Request):
    token = bearer(request.headers)
    court = (await asyncio.to_thread(authenticate_device, token))["quadra_id"]
    async with get_quadra_lock(court):
        ids_online = await hub.participantes_online(court)
        code, rec, state, applied = await asyncio.to_thread(
            apply_command, token, body, ids_online
        )
        if applied:
            await transmitir_estado(court, state)
    return JSONResponse(
        {"recibo": rec, "estado": state},
        status_code=code,
        headers={"Cache-Control": "no-store"},
    )
