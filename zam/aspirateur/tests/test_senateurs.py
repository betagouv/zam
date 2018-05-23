import os

import pytest


HERE = os.path.dirname(__file__)


@pytest.mark.parametrize('matricule,nom,groupe', [
    ('89017R', 'Adnot', 'NI'),
    ('08015R', 'Laurent', 'Les Républicains'),
])
def test_parse(matricule, nom, groupe):
    from zam_aspirateur.senateurs.parse import parse_senateurs

    filename = os.path.join(HERE, 'sample_data', 'ODSEN_GENERAL.csv')
    with open(filename, 'r', encoding='cp1252') as file_:
        senateurs_by_matricule = parse_senateurs(file_)

    senateur = senateurs_by_matricule[matricule]

    assert senateur.nom == nom
    assert senateur.groupe == groupe
