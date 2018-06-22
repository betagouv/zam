from zam_repondeur.models import AVIS


def normalize_num(num: str) -> int:
    try:
        num_int = int(num)
    except ValueError:
        num_int = int(num.split("\n")[0].strip(","))
    return num_int


def normalize_avis(avis: str) -> str:
    avis = avis.strip()
    avis_lower = avis.lower()
    if avis_lower in ("défavorable", "defavorable"):
        avis = "Défavorable"
    elif avis_lower in ("favorable",):
        avis = "Favorable"
    elif avis_lower in ("sagesse",):
        avis = "Sagesse"
    elif avis_lower in ("retrait",):
        avis = "Retrait"
    if avis and avis not in AVIS:
        pass  # print(avis)
    return avis


def normalize_reponse(reponse: str, previous_reponse: str) -> str:
    reponse = reponse.strip()
    if reponse.lower() == "id.":
        reponse = previous_reponse
    return reponse
