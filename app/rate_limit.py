import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class TentativasRegistro:
    falhas: list[float] = field(default_factory=list)
    bloqueado_ate: float = 0.0


class RateLimiter:
    def __init__(
        self,
        max_tentativas: int = 5,
        janela_segundos: float = 600.0,
        bloqueio_segundos: float = 300.0,
    ):
        self.max_tentativas = max_tentativas
        self.janela_segundos = janela_segundos
        self.bloqueio_segundos = bloqueio_segundos
        self._registros: dict[str, TentativasRegistro] = defaultdict(TentativasRegistro)
        self._lock = threading.Lock()

    def esta_bloqueado(
        self, chave: str, agora: float | None = None
    ) -> tuple[bool, int]:
        """Verifica se a chave está temporariamente bloqueada.

        Retorna (bloqueado, segundos_restantes).
        """
        if agora is None:
            agora = time.time()
        with self._lock:
            reg = self._registros.get(chave)
            if not reg:
                return False, 0
            if reg.bloqueado_ate > agora:
                restante = int(reg.bloqueado_ate - agora) + 1
                return True, restante
            return False, 0

    def registrar_falha(
        self, chave: str, agora: float | None = None
    ) -> tuple[bool, int]:
        """Registra uma tentativa com falha para a chave.

        Se o número de falhas na janela atingir o limite, ativa o bloqueio.
        Retorna (foi_bloqueado_agora, segundos_bloqueio).
        """
        if agora is None:
            agora = time.time()
        with self._lock:
            reg = self._registros[chave]
            limite_janela = agora - self.janela_segundos
            reg.falhas = [t for t in reg.falhas if t > limite_janela]
            reg.falhas.append(agora)

            if len(reg.falhas) >= self.max_tentativas:
                reg.bloqueado_ate = agora + self.bloqueio_segundos
                return True, int(self.bloqueio_segundos)
            return False, 0

    def registrar_sucesso(self, chave: str) -> None:
        """Limpa as tentativas acumuladas da chave após sucesso."""
        with self._lock:
            if chave in self._registros:
                del self._registros[chave]

    def resetar(self) -> None:
        """Limpa todos os registros (útil para testes)."""
        with self._lock:
            self._registros.clear()


owner_rate_limiter = RateLimiter(
    max_tentativas=5,
    janela_segundos=600.0,
    bloqueio_segundos=300.0,
)
