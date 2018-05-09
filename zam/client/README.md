# Client (means frontend for ministers and their teams)

## Installing

1.  Go to the `client` folder
2.  Create the virtualenv `python3 -m venv ~/.virtualenvs/zam`
3.  Activate it `source ~/.virtualenvs/zam/bin/activate.fish`
4.  Install dependecies `pip install -r requirements.txt`

## Generating

Adapt your paths for sensitive informations.

    python . generate path/to/Archives\ PLFSS/ path/to/target/

⚠️ Never ever commit/push the generated folder/file.

## Debugging

Most of the time, parsing only a few articles is enough:

    python . generate path/to/Archives\ PLFSS/ path/to/target/ --limit=8

You have a list of options with:

    python . generate --help
