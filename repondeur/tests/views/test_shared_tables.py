def test_get_shared_tables_empty(app, lecture_an, amendements_an, user_david):
    resp = app.get(f"/lectures/an.15.269.PO717460/options", user=user_david)

    assert resp.status_code == 200
    assert "Test table" not in resp.text
    assert "Aucune boîte personnalisée n’existe pour l’instant." in resp.text


def test_get_shared_tables_list(
    app, lecture_an, amendements_an, user_david, shared_table_lecture_an
):
    resp = app.get(f"/lectures/an.15.269.PO717460/options", user=user_david)

    assert resp.status_code == 200
    assert "Test table" in resp.text
    assert "Aucune boîte personnalisée n’existe pour l’instant." not in resp.text


def test_get_shared_tables_create_form(app, lecture_an, amendements_an, user_david):
    resp = app.get(f"/lectures/an.15.269.PO717460/boites/add", user=user_david)

    assert resp.status_code == 200
    assert "Créer une boîte" in resp.text


def test_post_shared_tables_create_form(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models import DBSession, SharedTable

    resp = app.get(f"/lectures/an.15.269.PO717460/boites/add", user=user_david)
    form = resp.form
    form["titre"] = "Test table"
    resp = form.submit()

    assert resp.status_code == 302
    assert (
        resp.location
        == "https://zam.test/lectures/an.15.269.PO717460/options#shared-tables"
    )

    resp = resp.follow()
    assert resp.status_code == 200
    assert "Test table" in resp.text

    shared_table = (
        DBSession.query(SharedTable).filter(SharedTable.titre == "Test table").one()
    )
    assert shared_table.slug == "test-table"
    assert shared_table.lecture.pk == lecture_an.pk


def test_get_shared_tables_edit_form(
    app, lecture_an, amendements_an, user_david, shared_table_lecture_an
):
    resp = app.get(f"/lectures/an.15.269.PO717460/boites/test-table/", user=user_david)

    assert resp.status_code == 200
    assert "Éditer cette boîte" in resp.text


def test_post_shared_tables_edit_form(
    app, lecture_an, amendements_an, user_david, shared_table_lecture_an
):
    from zam_repondeur.models import DBSession, SharedTable

    resp = app.get(f"/lectures/an.15.269.PO717460/boites/test-table/", user=user_david)
    form = resp.form
    form["titre"] = "Test table 2"
    resp = form.submit()

    assert resp.status_code == 302
    assert (
        resp.location
        == "https://zam.test/lectures/an.15.269.PO717460/options#shared-tables"
    )

    resp = resp.follow()
    assert resp.status_code == 200
    assert "Test table 2" in resp.text

    shared_table = (
        DBSession.query(SharedTable).filter(SharedTable.titre == "Test table 2").one()
    )
    assert shared_table.slug == "test-table-2"
    assert shared_table.lecture.pk == lecture_an.pk


def test_get_shared_tables_delete_form(
    app, lecture_an, amendements_an, user_david, shared_table_lecture_an
):
    resp = app.get(
        f"/lectures/an.15.269.PO717460/boites/test-table/delete", user=user_david
    )

    assert resp.status_code == 200
    assert "Supprimer la boîte « Test table »" in resp.text


def test_post_shared_tables_delete_form(
    app, lecture_an, amendements_an, user_david, shared_table_lecture_an
):
    from zam_repondeur.models import DBSession, SharedTable

    assert (
        DBSession.query(SharedTable).filter(SharedTable.titre == "Test table").count()
        == 1
    )
    resp = app.get(
        f"/lectures/an.15.269.PO717460/boites/test-table/delete", user=user_david
    )
    resp = resp.form.submit()

    assert resp.status_code == 302
    assert (
        resp.location
        == "https://zam.test/lectures/an.15.269.PO717460/options#shared-tables"
    )

    resp = resp.follow()
    assert resp.status_code == 200
    assert "Test table" in resp.text  # From notification.
    assert (
        DBSession.query(SharedTable).filter(SharedTable.titre == "Test table").count()
        == 0
    )
