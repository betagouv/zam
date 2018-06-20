from zam_repondeur.models import AVIS, Amendement, DBSession


def normalize_num(num):
    try:
        num = int(num)
    except ValueError:
        num = int(num.split("\n")[0].strip(","))
    return num


def normalize_avis(avis):
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


def normalize_reponse(reponse, previous_reponse, lecture):
    reponse = reponse.strip()
    if reponse.startswith("id."):
        if reponse == "id.":
            reponse = previous_reponse
        else:
            id_, num, name = reponse.split(" ")
            amendement = (
                DBSession.query(Amendement)
                .filter(
                    Amendement.chambre == lecture.chambre,
                    Amendement.session == lecture.session,
                    Amendement.num_texte == lecture.num_texte,
                    Amendement.num == num,
                )
                .first()
            )
            if amendement:
                reponse = amendement.reponse
    return reponse
