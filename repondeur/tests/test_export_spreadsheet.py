import csv
from pathlib import Path


def test_export_csv_columns(lecture_an, article1_an, tmpdir):
    from zam_repondeur.export.spreadsheet import write_csv
    from zam_repondeur.models import DBSession, Amendement

    filename = str(tmpdir.join("test.csv"))

    amendement = Amendement.create(
        lecture=lecture_an,
        article=article1_an,
        num=333,
        position=1,
        avis="Favorable",
        objet="Un objet très pertinent",
        reponse="Une réponse très appropriée",
        comments="Avec des commentaires",
    )
    DBSession.add(amendement)
    DBSession.add(lecture_an)

    counter = write_csv(lecture_an, filename, request={})

    assert counter["amendements"] == 1

    with Path(filename).open(encoding="utf-8-sig") as csv_file:
        reader = csv.reader(csv_file, delimiter=";")
        headers = next(reader)
        assert headers == [
            "Num article",
            "Titre article",
            "Num amdt",
            "Rectif",
            "Parent (sous-amdt)",
            "Auteur",
            "Groupe",
            "Gouvernemental",
            "Corps amdt",
            "Exposé amdt",
            "Identique",
            "Avis du Gouvernement",
            "Objet amdt",
            "Réponse",
            "Commentaires",
            "Affectation (email)",
            "Affectation (nom)",
            "Sort",
        ]


def test_export_excel_columns(lecture_an, article1_an, tmpdir):
    from openpyxl import load_workbook

    from zam_repondeur.export.spreadsheet import write_xlsx
    from zam_repondeur.models import DBSession, Amendement

    filename = str(tmpdir.join("test.xlsx"))

    amendement = Amendement.create(
        lecture=lecture_an,
        article=article1_an,
        num=333,
        position=1,
        avis="Favorable",
        objet="Un objet très pertinent",
        reponse="Une réponse très appropriée",
        comments="Avec des commentaires",
    )
    DBSession.add(amendement)
    DBSession.add(lecture_an)

    counter = write_xlsx(lecture_an, filename, request={})

    assert counter["amendements"] == 1

    wb = load_workbook(filename, read_only=True)
    ws = wb.active
    header_row = next(ws.rows)
    headers = [cell.value for cell in header_row]

    assert headers == [
        "Num article",
        "Titre article",
        "Num amdt",
        "Rectif",
        "Parent (sous-amdt)",
        "Auteur",
        "Groupe",
        "Gouvernemental",
        "Corps amdt",
        "Exposé amdt",
        "Identique",
        "Avis du Gouvernement",
        "Objet amdt",
        "Réponse",
        "Commentaires",
        "Affectation (email)",
        "Affectation (nom)",
        "Sort",
    ]


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

    counter = write_csv(lecture_an, filename, request={})

    assert counter["amendements"] == 2

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

    counter = write_csv(lecture_an, filename, request={})

    assert counter["amendements"] == 2

    with Path(filename).open(encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=";")
        amendement1 = next(reader)
        assert amendement1["Auteur"] == "Victor Hugo"
        amendement2 = next(reader)
        assert amendement2["Auteur"] == ""


def test_export_csv_with_gouvernemental(lecture_an, article1_an, tmpdir):
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
    amendements[0].gouvernemental = True
    DBSession.add_all(amendements)
    DBSession.add(lecture_an)

    counter = write_csv(lecture_an, filename, request={})

    assert counter["amendements"] == 2

    with Path(filename).open(encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=";")
        amendement1 = next(reader)
        assert amendement1["Gouvernemental"] == "Oui"
        amendement2 = next(reader)
        assert amendement2["Gouvernemental"] == "Non"


def test_export_csv_with_identique(lecture_an, article1_an, tmpdir):
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
        for position, num in enumerate((333, 444, 777), 1)
    ]
    amendements[0].id_identique = 42
    amendements[1].id_identique = 42
    DBSession.add_all(amendements)
    DBSession.add(lecture_an)

    counter = write_csv(lecture_an, filename, request={})

    assert counter["amendements"] == 3

    with Path(filename).open(encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=";")
        amendement1 = next(reader)
        assert amendement1["Identique"] == "333"
        amendement2 = next(reader)
        assert amendement2["Identique"] == "333"
        amendement3 = next(reader)
        assert amendement3["Identique"] == ""
