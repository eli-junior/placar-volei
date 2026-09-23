"""Habilita o teste pessoal sem expor o segredo do owner no site ou no APK."""

import argparse
import getpass
import json
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("server", help="Origem HTTPS do placar (HTTP apenas local)")
    parser.add_argument("court", help="PIN da sala já criada por eli")
    parser.add_argument("--disable", action="store_true")
    args = parser.parse_args()
    server = args.server.rstrip("/")
    address = urlparse(server)
    if (
        address.scheme not in ("https", "http")
        or not address.hostname
        or address.username
        or address.password
        or address.query
        or address.fragment
        or address.path
        or (
            address.scheme == "http"
            and address.hostname not in ("localhost", "127.0.0.1", "::1")
        )
    ):
        parser.error("Use uma origem HTTPS ou HTTP local, sem segredo na URL.")
    secret = getpass.getpass("Segredo do owner (não será exibido): ")

    # A URL é explícita para evitar que o segredo siga redirecionamentos.
    from urllib.request import HTTPRedirectHandler, build_opener

    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    opener = build_opener(NoRedirect)
    try:
        with opener.open(
            Request(f"{server}/api/owner/quadras", headers={"x-owner-secret": secret}),
            timeout=15,
        ) as response:
            rooms = json.load(response)["quadras"]
        room = next((room for room in rooms if room["id"] == args.court), None)
        if room is None:
            parser.error("Sala não encontrada.")
        # A lista pública basta para localizar a identidade; habilitar exige owner.
        with urlopen(
            f"{server}/api/quadras/{args.court}/participantes", timeout=15
        ) as response:
            participants = json.load(response)["participantes"]
        eli = next((p for p in participants if p["apelido"] == "eli"), None)
        if eli is None:
            parser.error("Entre na sala com o apelido eli antes de habilitar.")
        payload = json.dumps(
            {"participant_id": eli["id"], "enabled": not args.disable}
        ).encode()
        with opener.open(
            Request(
                f"{server}/api/owner/watch-access",
                data=payload,
                headers={"x-owner-secret": secret, "Content-Type": "application/json"},
            ),
            timeout=15,
        ) as response:
            enabled = json.load(response)["enabled"]
        print(
            "Relógio habilitado nesta sala."
            if enabled
            else "Acesso de relógio desabilitado nesta sala."
        )
    except HTTPError as error:
        # Nunca imprimir cabeçalhos ou o segredo informado.
        print(
            f"Servidor recusou a operação (HTTP {error.code}). Confira sala, permissão e segredo."
        )
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
