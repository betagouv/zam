import os

import pytest


HERE = os.path.dirname(__file__)


@pytest.mark.parametrize('nom,groupe', [
    ('M. ABADIE', 'RDSE'),
    ('M. ABADIE', 'RDSE'),
    ('M. DANIEL LAURENT', 'Les Républicains'),
])
def test_parse(nom, groupe):
    from senateurs.parse import parse_senateurs
    filename = os.path.join(HERE, 'sample_data', 'ODSEN_GENERAL.csv')
    with open(filename, 'r', encoding='cp1252') as file_:
        senateurs_by_name = parse_senateurs(file_)
    senateur = senateurs_by_name[nom]
    assert senateur.groupe == groupe
