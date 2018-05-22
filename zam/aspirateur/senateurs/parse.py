import csv

from .models import Senateur


def parse_senateurs(iterable):
    lines = (
        line
        for line in iterable
        if not line.startswith('%')
    )
    senateurs = [
        Senateur(
            qualite=row['Qualité'],
            nom=row['Nom usuel'],
            prenom=row['Prénom usuel'],
            groupe=row['Groupe politique'],
        )
        for row in csv.DictReader(lines)
    ]
    by_name = {}
    for s in senateurs:
        by_name[f"{s.qualite} {s.nom}".upper()] = s
        by_name[f"{s.qualite} {s.prenom} {s.nom}".upper()] = s
    return by_name
