"""Fila e reis para quem acompanha a quadra (CV8.DS5.US13).

Projeta o estado completo da sessão (que só o dono vê) na parte pública: quem
está em quadra, a fila de espera e os reis, só com nomes curtos, vitórias e
posições. Nada de notas, presença, ids ou saldo. Vai para a sala da quadra
vinculada: no `ESTADO_INICIAL` e a cada mudança do gerenciador.
"""

from app.conducao import nome_da_equipe, nomes_curtos


def projetar(estado: dict) -> dict | None:
    """None quando não há nada a mostrar (sem rodada nem campeão recente)."""
    rodada = estado.get("rodada")
    conducao = estado.get("conducao")
    if rodada and rodada["estado"] == "em_andamento" and conducao:
        curtos = nomes_curtos([j for t in rodada["times"] for j in t["jogadores"]])

        def equipe(time: dict) -> dict:
            nomes = [curtos[j["id"]] for j in time["jogadores"]]
            return {
                "time": time["fila"],
                "nome": nome_da_equipe(nomes),
                "vitorias": time.get("vitorias", 0),
                "incompleto": bool(time["incompleto"]),
            }

        return {
            "rodada": rodada["numero"],
            "fase": conducao["fase"],
            "em_quadra": [equipe(t) for t in conducao["em_quadra"]],
            "fila": [equipe(t) for t in conducao["fila"]],
            "reis": [equipe(t) for t in conducao["reis"]],
            "campeao": None,
        }
    campeao = estado.get("ultimo_campeao")
    if campeao:
        return {
            "rodada": campeao["rodada"],
            "fase": "campeao",
            "em_quadra": [],
            "fila": [],
            "reis": [],
            "campeao": {
                "time": campeao["time"],
                "nome": " + ".join(n.split()[0] for n in campeao["jogadores"]),
            },
        }
    return None
