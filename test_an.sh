#!/bin/bash -e

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

message() {
    echo
    echo -e "${GREEN}>>> $1${NC}"
}

VENVS=/tmp/zamtest/virtualenvs
mkdir -p "$VENVS"

OUTPUT=/tmp/zamtest/output
mkdir -p "$OUTPUT"

message "Installation de l'aspirateur"
[[ ! -d "$VENVS/aspirateur" ]] && python3 -m venv "$VENVS/aspirateur"
pushd aspirateur > /dev/null
PIP="$VENVS/aspirateur/bin/pip"
$PIP install --quiet --upgrade pip
[[ -f requirements.txt ]] && $PIP install --quiet -r requirements.txt
[[ -f requirements-dev.txt ]] && $PIP install --quiet -r requirements-dev.txt
$PIP install --quiet .
popd > /dev/null

message "Installation de la visionneuse"
[[ ! -d "$VENVS/visionneuse" ]] && python3 -m venv "$VENVS/visionneuse"
pushd visionneuse > /dev/null
PIP="$VENVS/visionneuse/bin/pip"
$PIP install --quiet --upgrade pip
[[ -f requirements.txt ]] && $PIP install --quiet -r requirements.txt
[[ -f requirements-dev.txt ]] && $PIP install --quiet -r requirements-dev.txt
$PIP install --quiet .
popd > /dev/null

message "Installation du parser de la fabrique de la loi"
[[ ! -d "$VENVS/tlfp" ]] && python3 -m venv "$VENVS/tlfp"
PIP="$VENVS/tlfp/bin/pip"
$PIP install --quiet --upgrade pip
$PIP install --quiet -e git+https://github.com/regardscitoyens/anpy.git#egg=anpy
$PIP install --quiet -e git+https://github.com/regardscitoyens/legipy.git#egg=legipy
$PIP install --quiet -e git+https://framagit.org/mdamien/metslesliens.git@1.1.1-manifest#egg=metslesliens
$PIP install --quiet -e git+https://github.com/regardscitoyens/the-law-factory-parser.git#egg=tlfp

message "Lancement de l'aspirateur"
"$VENVS/aspirateur/bin/zam-aspirateur" --source=an --session=15 --texte=0269 --output-format=json --output="$OUTPUT/amendements_15_0269.json"

message "Lancement du parser de la fabrique de la loi"
"$VENVS/tlfp/bin/tlfp-parse-text" http://www.assemblee-nationale.fr/15/projets/pl0269.asp >"$OUTPUT/articles-an-plfss2018.json"

message "Lancement de la visionneuse"
"$VENVS/visionneuse/bin/zam-visionneuse" --file-aspirateur="$OUTPUT/amendements_15_0269.json" --file-reponses="../Archives PLFSS 2018/JSON - fichier de sauvegarde/AN2-2018.json" --folder-jaunes="../Archives PLFSS 2018/Jeu de docs - PDF, word/AN2/" --file-articles="$OUTPUT/articles-an-plfss2018.json" --folder-output="$OUTPUT"

message "Vérification de la sortie de la visionneuse"
"$VENVS/visionneuse/bin/pytest" visionneuse/tests/test_output.py
