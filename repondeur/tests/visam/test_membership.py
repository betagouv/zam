def test_membership_direct_access(org_cgt, user_ccfp):
    from zam_repondeur.models import DBSession

    DBSession.add(org_cgt)
    DBSession.add(user_ccfp)

    assert [membership.user for membership in org_cgt.memberships] == [user_ccfp]
    assert [membership.organisation for membership in user_ccfp.memberships] == [
        org_cgt
    ]


def test_membership_chambre_default(user_david):
    from zam_repondeur.models import DBSession

    DBSession.add(user_david)

    assert user_david.chambres == []


def test_membership_chambre_defined(user_ccfp):
    from zam_repondeur.models import Chambre, DBSession

    DBSession.add(user_ccfp)

    assert user_ccfp.chambres == [Chambre.CCFP]


def test_membership_organisation_cgt(org_cgt, user_ccfp):
    from zam_repondeur.models import DBSession

    DBSession.add(org_cgt)
    DBSession.add(user_ccfp)

    assert org_cgt.members == [user_ccfp]
    assert user_ccfp.organisations == [org_cgt]


def test_membership_organisation_gouvernement(org_gouvernement, user_ccfp_gouvernement):
    from zam_repondeur.models import DBSession

    DBSession.add(org_gouvernement)
    DBSession.add(user_ccfp_gouvernement)

    assert org_gouvernement.members == [user_ccfp_gouvernement]
    assert user_ccfp_gouvernement.organisations == [org_gouvernement]
