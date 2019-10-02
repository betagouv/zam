from pathlib import Path

import pytest

HERE = Path(__file__)
SAMPLE_DATA_DIR = HERE.parent / "sample_data" / "senat"


@pytest.mark.parametrize(
    "matricule,nom,groupe",
    [("89017R", "Adnot", "NI"), ("08015R", "Laurent", "Les Républicains")],
)
def test_parse(matricule, nom, groupe):
    from zam_repondeur.services.fetch.senat.senateurs.parse import parse_senateurs

    filename = SAMPLE_DATA_DIR / "ODSEN_GENERAL.csv"
    with filename.open("r", encoding="cp1252") as file_:
        senateurs_by_matricule = parse_senateurs(file_)

    senateur = senateurs_by_matricule[matricule]

    assert senateur.nom == nom
    assert senateur.groupe == groupe
