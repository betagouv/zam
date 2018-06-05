import os

import pytest


def test_get_list_empty(app):

    resp = app.get("/lectures/")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert "Aucune lecture pour l'instant." in resp.text


@pytest.yield_fixture
def dummy_lecture(app):
    data_dir = app.app.registry.settings["zam.data_dir"]
    dir_names = ["senat-2017-2018-63", "ignore_this"]
    paths = [os.path.join(data_dir, dir_name) for dir_name in dir_names]
    for path in paths:
        os.makedirs(path)
    yield
    for path in paths:
        os.rmdir(path)


def test_get_list_not_empty(app, dummy_lecture):

    resp = app.get("/lectures/")

    assert resp.status_code == 200
    assert resp.content_type == "text/html"

    assert "Sénat, session 2017-2018, texte nº 63" in resp.text
