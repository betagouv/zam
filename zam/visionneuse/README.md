# Visionneuse (means frontend for ministers and their teams)

## Requirements

*   Python 3.6+

## Installing

1.  Go to the `visionneuse` folder
2.  Create the virtualenv `python3 -m venv ~/.virtualenvs/zam-visionneuse`
3.  Activate it `source ~/.virtualenvs/zam-visionneuse/bin/activate.fish`
4.  Install dependecies `pip install -r requirements.txt`

## Generating

Set your paths for sensitive informations, for instance with fish:

    set -gx ZAM_ASPIRATEUR_SOURCE path/to/zam/aspirateur/amendements_2017-2018_63.json
    set -gx ZAM_DRUPAL_SOURCE path/to/Archives\ PLFSS\ 2018/JSON\ -\ fichier\ de\ sauvegarde/Sénat1-2018.json
    set -gx ZAM_JAUNES_SOURCE path/to/Archives\ PLFSS\ 2018/Jeu\ de\ docs\ -\ PDF,\ word/Sénat1/
    set -gx ZAM_OUTPUT path/to/target/

Then launch the generator:

    python . generate

⚠️ Never ever commit/push the generated folder/file.

## Debugging

Most of the time, parsing only a few articles is enough:

    python . generate --limit=8

You have a list of options with:

    python . generate --help

## Testing

First, set environment variables as described in `Generating` above.

    pip install pytest selectolax
    env PYTHONPATH=. pytest
