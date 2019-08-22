import transaction


def test_get_shared_tables_empty(app, lecture_an, amendements_an, user_david):
    resp = app.get(
        f"/dossiers/plfss-2018/lectures/an.15.269.PO717460/options", user=user_david
    )

    assert resp.status_code == 200
    assert "Test table" not in resp.text
    assert "Aucune boîte n’a été créée." in resp.text


def test_get_shared_tables_list(
    app, lecture_an, amendements_an, user_david, shared_table_lecture_an
):
    resp = app.get(
        f"/dossiers/plfss-2018/lectures/an.15.269.PO717460/options", user=user_david
    )

    assert resp.status_code == 200
    assert "Test table" in resp.text
    assert "Aucune boîte n’a été créée." not in resp.text


def test_get_shared_tables_create_form(app, lecture_an, amendements_an, user_david):
    resp = app.get(
        f"/dossiers/plfss-2018/lectures/an.15.269.PO717460/boites/add", user=user_david
    )

    assert resp.status_code == 200
    assert "Créer une boîte" in resp.text


def test_post_shared_tables_create_form(app, lecture_an, amendements_an, user_david):
    from zam_repondeur.models import DBSession, Lecture, SharedTable

    with transaction.manager:
        DBSession.add(user_david)

    resp = app.get(
        f"/dossiers/plfss-2018/lectures/an.15.269.PO717460/boites/add", user=user_david
    )
    form = resp.form
    form["titre"] = "Test table"
    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == (
        "https://zam.test"
        "/dossiers/plfss-2018"
        "/lectures/an.15.269.PO717460"
        "/options#shared-tables"
    )

    resp = resp.follow()
    assert resp.status_code == 200
    assert "Test table" in resp.text

    shared_table = (
        DBSession.query(SharedTable).filter(SharedTable.titre == "Test table").one()
    )
    assert shared_table.slug == "test-table"
    assert shared_table.lecture.pk == lecture_an.pk

    # A dedicated event should be created.
    lecture_an = Lecture.get_by_pk(lecture_an.pk)  # refresh object
    assert len(lecture_an.events) == 1
    assert lecture_an.events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> "
        "a créé la boîte « Test table »"
    )


def test_get_shared_tables_edit_form(
    app, lecture_an, amendements_an, user_david, shared_table_lecture_an
):
    resp = app.get(
        f"/dossiers/plfss-2018/lectures/an.15.269.PO717460/boites/test-table/",
        user=user_david,
    )

    assert resp.status_code == 200
    assert "Éditer cette boîte" in resp.text
    assert "Supprimer" in resp.text
    assert "button button-sm danger" in resp.text


def test_get_shared_tables_edit_form_has_active_delete_link_if_no_amendement(
    app, lecture_an, amendements_an, user_david, shared_table_lecture_an
):
    resp = app.get(
        f"/dossiers/plfss-2018/lectures/an.15.269.PO717460/boites/test-table/",
        user=user_david,
    )

    assert resp.status_code == 200
    assert "Supprimer" in resp.text
    assert "button button-sm danger" in resp.text


def test_get_shared_tables_edit_form_has_disabled_delete_link_if_amendement(
    app, lecture_an, amendements_an, user_david, shared_table_lecture_an
):
    from zam_repondeur.models import DBSession

    with transaction.manager:
        DBSession.add(shared_table_lecture_an)
        shared_table_lecture_an.amendements.append(amendements_an[0])

    resp = app.get(
        f"/dossiers/plfss-2018/lectures/an.15.269.PO717460/boites/test-table/",
        user=user_david,
    )

    assert resp.status_code == 200
    assert "Supprimer" in resp.text
    assert "button button-sm disabled" in resp.text


def test_post_shared_tables_edit_form(
    app, lecture_an, amendements_an, user_david, shared_table_lecture_an
):
    from zam_repondeur.models import DBSession, Lecture, SharedTable

    with transaction.manager:
        DBSession.add(user_david)

    resp = app.get(
        f"/dossiers/plfss-2018/lectures/an.15.269.PO717460/boites/test-table/",
        user=user_david,
    )
    form = resp.form
    form["titre"] = "Test table 2"
    resp = form.submit()

    assert resp.status_code == 302
    assert resp.location == (
        "https://zam.test"
        "/dossiers/plfss-2018"
        "/lectures/an.15.269.PO717460"
        "/options#shared-tables"
    )

    resp = resp.follow()
    assert resp.status_code == 200
    assert "Test table 2" in resp.text

    shared_table = (
        DBSession.query(SharedTable).filter(SharedTable.titre == "Test table 2").one()
    )
    assert shared_table.slug == "test-table-2"
    assert shared_table.lecture.pk == lecture_an.pk

    # A dedicated event should be created.
    lecture_an = Lecture.get_by_pk(lecture_an.pk)  # refresh object
    assert len(lecture_an.events) == 1
    assert lecture_an.events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> "
        "a renommé la boîte « Test table » en « Test table 2 »"
    )


def test_get_shared_tables_delete_form(
    app, lecture_an, amendements_an, user_david, shared_table_lecture_an
):
    resp = app.get(
        f"/dossiers/plfss-2018/lectures/an.15.269.PO717460/boites/test-table/delete",
        user=user_david,
    )

    assert resp.status_code == 200
    assert "Supprimer la boîte « Test table »" in resp.text


def test_post_shared_tables_delete_form(
    app, lecture_an, amendements_an, user_david, shared_table_lecture_an
):
    from zam_repondeur.models import DBSession, Lecture, SharedTable

    with transaction.manager:
        DBSession.add(user_david)

    assert (
        DBSession.query(SharedTable).filter(SharedTable.titre == "Test table").count()
        == 1
    )
    resp = app.get(
        f"/dossiers/plfss-2018/lectures/an.15.269.PO717460/boites/test-table/delete",
        user=user_david,
    )
    resp = resp.form.submit()

    assert resp.status_code == 302
    assert resp.location == (
        "https://zam.test"
        "/dossiers/plfss-2018"
        "/lectures/an.15.269.PO717460"
        "/options#shared-tables"
    )

    resp = resp.follow()
    assert resp.status_code == 200
    assert "Test table" in resp.text  # From notification.
    assert (
        DBSession.query(SharedTable).filter(SharedTable.titre == "Test table").count()
        == 0
    )

    # A dedicated event should be created.
    lecture_an = Lecture.get_by_pk(lecture_an.pk)  # refresh object
    assert len(lecture_an.events) == 1
    assert lecture_an.events[0].render_summary() == (
        "<abbr title='david@exemple.gouv.fr'>David</abbr> "
        "a supprimé la boîte « Test table »"
    )
