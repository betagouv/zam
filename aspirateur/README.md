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
$ zam-aspirateur --source=senat --session=2017-2018 --texte=63
595 amendements écrits dans amendements_2017-2018_63.csv
```

Dans le cas d’une récupération d’amendements depuis le site de l’Assemblée Nationale,
les variables d’environnement `ZAM_AN_PATTERN_LISTE` et `ZAM_AN_PATTERN_AMENDEMENT`
doivent être définies, puis :

```
$ zam-aspirateur --source=an --session=14 --texte=4072
772 amendements écrits dans amendements_14_4072.csv
```

Le résultat sera un fichier CSV comprennant l'ensemble des amendements
déposés, triés par ordre de passage lors de la discussion en séance.

Les amendements non discutés (retirés ou irrecevables) sont regroupés
à la fin du tableau.

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
