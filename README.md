# zam

**Alléger la charge de préparation par le gouvernement du débat parlementaire.**

Le dépôt regroupe plusieurs applications distinctes (monorepo) :

* [`/aspirateur/`](aspirateur/) contient l’outil permettant de récupérer les données publiques/ouvertes issues des sites du Sénat et de l’Assemblée Nationale.
* [`/visionneuse/`](visionneuse/) contient l’outil permettant d’afficher les articles, amendements et réponses (ces dernières sont privées) de manière ergonomique.
* [`/repondeur/`](repondeur/) contient l'application web intégrant l'aspirateur et la visionneuse, ainsi que la préparation collaborative des réponses aux amendements.
* [`/admin/`](admin/) contient les tâches pour initialiser et déployer le serveur.

Chacune des application est documentée de manière plus précise au sein du fichier README dédié.
