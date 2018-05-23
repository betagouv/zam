# Aspirateur

## Description

Récupérer la liste des amendements relatifs à un texte de loi discuté au Sénat.

## Prérequis

Python 3.6+

## Installation

```
$ python -m venv ~/.virtualenvs/zam-aspirateur
$ source ~/.virtualenvs/zam-aspirateur/bin/activate
$ pip install -r requirements.txt -r requirements-dev.txt
$ pip install -e .
```

## Usage

Pour récupérer la liste des amendements au PLFSS 2018 lors de la première lecture au Sénat (texte nº63) :

```
$ zam-aspirateur --session=2017-2018 --texte=63
Wrote 595 rows to amendements_2017-2018_63.csv
```

Le résultat sera un fichier CSV comprenenant l'ensemble des amendements
déposés, triés par ordre de passage lors de la discussion en séance.

Les amendements non discutés (retirés ou irrecevables) sont regroupés
à la fin du tableau.

## Tests et analyses statiques du code

Lancer les tests:

```
$ pytest
```

Vérifier les règles de style:

```
$ flake8
```

Vérifier les annotations de type:

```
$ mypy zam_aspirateur
```
