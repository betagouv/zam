from dataclasses import dataclass


@dataclass
class Senateur:
    matricule: str
    qualite: str
    nom: str
    prenom: str
    groupe: str
