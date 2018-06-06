import os


def test_render_template():
    from zam_visionneuse.templates import render
    from zam_visionneuse.models import Articles, Reponses

    current_dir = os.getcwd()
    parent = os.path.dirname(current_dir)
    os.chdir(parent)
    html = render("Titre", Articles(), Reponses())
    os.chdir(current_dir)
