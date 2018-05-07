# zam

Alléger la charge de préparation par le gouvernement du débat parlementaire.

## Client (means frontend for ministers and their teams)

### Installing

    pipenv install --three
    pipenv shell

### Generating

Adapt your paths for sensitive informations.

    python zam/client/ generate ../Archives\ PLFSS/ > ../index.html

⚠️ Never ever commit/push the generated file.

### Debugging

    pipenv install --three --dev

Most of the time, parsing only a few articles is enough:

    python zam/client/ generate ../Archives\ PLFSS/ --limit=8 > ../index.html

You have a list of options with:

    python zam/client/ generate --help

Note that `ipdb` is installed too.
