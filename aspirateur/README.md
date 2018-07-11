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

## Tests et analyses statiques du code

Reformatter le code:

```
$ black .
```

Vérifier les règles de style:

```
$ flake8
```

Vérifier les annotations de type:

```
$ mypy zam_aspirateur
```

Lancer les tests:

```
$ pytest
```

Bonus : toutes les étapes précédentes en une seule commande :

```
$ tox
```
