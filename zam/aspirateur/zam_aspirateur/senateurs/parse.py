from typing import Dict, Iterable
import csv

from .models import Senateur


def parse_senateurs(iterable: Iterable[str]) -> Dict[str, Senateur]:
    lines = (
        line
        for line in iterable
        if not line.startswith('%')
    )
    senateurs = (
        Senateur(  # type: ignore
            matricule=row['Matricule'],
            qualite=row['Qualité'],
            nom=row['Nom usuel'],
            prenom=row['Prénom usuel'],
            groupe=row['Groupe politique'],
        )
        for row in csv.DictReader(lines)
    )
    by_matricule = {
        senateur.matricule: senateur
        for senateur in senateurs
    }
    return by_matricule
