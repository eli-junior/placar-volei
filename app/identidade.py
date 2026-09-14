import hashlib

# O cookie antigo continha uma credencial publicada nos IDs da versão 0.2.
SESSION_COOKIE = "placar_session_v3"


def hash_sessao(session_id: str) -> str:
    return hashlib.sha256(session_id.encode()).hexdigest()
