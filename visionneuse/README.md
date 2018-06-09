# Visionneuse (means frontend for ministers and their teams)

## Requirements

*   Python 3.6+

## Installing

1.  Go to the `visionneuse` folder
2.  Create the virtualenv `python3 -m venv ~/.virtualenvs/zam-visionneuse`
3.  Activate it `source ~/.virtualenvs/zam-visionneuse/bin/activate.fish`
4.  Install dependecies `pip install -r requirements.txt`
5.  Run `pip install -e .`

## Generating

Generate JSON files related to amendements from the aspirateur and articles from tlfp:

    zam-aspirateur --source=senat --session=2017-2018 --texte=63
    tlfp-parse-text http://www.senat.fr/leg/pjl17-063.html > articles-senat-plfss2018.json

Then launch the generator:

    zam-visionneuse --file-aspirateur=path/to/zam/aspirateur/amendements_2017-2018_63.json --file-reponses=path/to/Archives\ PLFSS\ 2018/JSON\ -\ fichier\ de\ sauvegarde/Sénat1-2018.json --folder-jaunes=path/to/Archives\ PLFSS\ 2018/Jeu\ de\ docs\ -\ PDF,\ word/Sénat1/ --file-articles path/to/articles-senat-plfss2018.json --folder-output path/to/target/

⚠️ Never ever commit/push the generated folder/file.


## Testing

First, set environment variables as described in `Generating` above.

    pip install -r requirements-dev.txt
    pytest
