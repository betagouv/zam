import csv
from pathlib import Path


def test_export_csv_with_parent(lecture_an, article1_an, tmpdir):
    from zam_repondeur.export.spreadsheet import write_csv
    from zam_repondeur.models import DBSession, Amendement

    filename = str(tmpdir.join("test.csv"))

    amendements = [
        Amendement.create(
            lecture=lecture_an,
            article=article1_an,
            num=num,
            position=position,
            avis="Favorable",
            objet="Un objet très pertinent",
            reponse="Une réponse très appropriée",
            comments="Avec des commentaires",
        )
        for position, num in enumerate((333, 777), 1)
    ]
    amendements[1].parent = amendements[0]
    DBSession.add_all(amendements)
    DBSession.add(lecture_an)

    nb_rows = write_csv(lecture_an, filename, request={})

    assert nb_rows == 2

    with Path(filename).open(encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=";")
        amendement1 = next(reader)
        assert amendement1["Parent (sous-amdt)"] == ""
        amendement2 = next(reader)
        assert amendement2["Parent (sous-amdt)"] == "333"


def test_export_csv_with_auteur(lecture_an, article1_an, tmpdir):
    from zam_repondeur.export.spreadsheet import write_csv
    from zam_repondeur.models import DBSession, Amendement

    filename = str(tmpdir.join("test.csv"))

    amendements = [
        Amendement.create(
            lecture=lecture_an,
            article=article1_an,
            num=num,
            position=position,
            avis="Favorable",
            objet="Un objet très pertinent",
            reponse="Une réponse très appropriée",
            comments="Avec des commentaires",
        )
        for position, num in enumerate((333, 777), 1)
    ]
    amendements[0].auteur = "Victor Hugo"
    DBSession.add_all(amendements)
    DBSession.add(lecture_an)

    nb_rows = write_csv(lecture_an, filename, request={})

    assert nb_rows == 2

    with Path(filename).open(encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=";")
        amendement1 = next(reader)
        assert amendement1["Auteur"] == "Victor Hugo"
        amendement2 = next(reader)
        assert amendement2["Auteur"] == ""
