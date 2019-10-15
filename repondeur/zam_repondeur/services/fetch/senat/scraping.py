import logging
import re
from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Dict, Optional, Set

from bs4 import BeautifulSoup, element

from zam_repondeur.models.organe import ORGANE_SENAT
from zam_repondeur.models.phase import Phase
from zam_repondeur.services.fetch.an.dossiers.models import (
    Chambre,
    DossierRef,
    DossierRefsByUID,
    LectureRef,
    TexteRef,
    TypeTexte,
)
from zam_repondeur.services.fetch.http import get_http_session
from zam_repondeur.slugs import slugify

logger = logging.getLogger(__name__)


BASE_URL_SENAT = "https://www.senat.fr"
TEXTES_RECENTS_URL = f"{BASE_URL_SENAT}/dossiers-legislatifs/textes-recents.html"


def get_dossiers_senat() -> DossierRefsByUID:
    html = download_textes_recents()
    webpages_urls = extract_recent_urls(html)
    pids_rss = convert_to_rss_urls(webpages_urls)
    dossier_refs_by_uid = {
        dossier_id: create_dossier(dossier_id, rss_url)
        for dossier_id, rss_url in pids_rss.items()
    }
    return dossier_refs_by_uid


def download_textes_recents() -> str:
    http_session = get_http_session()
    resp = http_session.get(TEXTES_RECENTS_URL)
    if resp.status_code != HTTPStatus.OK:
        raise RuntimeError("Failed to download textes recents from senat.fr")

    content: str = resp.text
    return content


def extract_recent_urls(html: str) -> Set[str]:
    soup = BeautifulSoup(html, "html5lib")
    next_textes_box = soup.select(".box.box-type-02")[0]
    return {
        link.attrs.get("href", "")
        for link in next_textes_box.select("a")
        if "/dossier-legislatif/" in link.attrs.get("href", "")
    }


def scrape_dossier(dossier_id: str) -> DossierRef:
    rss_url = build_rss_url(dossier_id)
    return create_dossier(dossier_id, rss_url)


def convert_to_rss_urls(webpages_urls: Set[str]) -> Dict[str, str]:
    dossier_ids = (extract_dossier_id(url) for url in webpages_urls)
    return {dossier_id: build_rss_url(dossier_id) for dossier_id in dossier_ids}


def extract_dossier_id(webpage_url: str) -> str:
    prefix = len("/dossier-legislatif/")
    suffix = len(".html")
    return webpage_url[prefix:-suffix]


def build_rss_url(dossier_id: str) -> str:
    return f"/dossier-legislatif/rss/dosleg{dossier_id}.xml"


def create_dossier(dossier_id: str, rss_url: str) -> DossierRef:
    rss_content = download_rss(rss_url)
    soup = BeautifulSoup(rss_content, "html5lib")
    prefix = len("Sénat - ")
    title = soup.title.string[prefix:]
    slug = slugify(title)
    # We cast the bs4 output explicitly to a string because of something
    # related to https://bugs.python.org/issue1757057
    # Once pickled to put in Redis, it would otherwise raise a RecursionError.
    senat_url = str(soup.id.string)
    # URLs in Senat's own feeds are actually redirections.
    senat_url = senat_url.replace("dossierleg", "dossier-legislatif")
    prev_texte: Optional[TexteRef] = None
    lectures = []
    entries = sorted(soup.select("entry"), key=lambda e: e.created.string)
    for entry in entries:
        lecture = create_lecture(dossier_id, entry, prev_texte=prev_texte)
        if lecture is not None:
            prev_texte = lecture.texte
            lectures.append(lecture)
    dossier = DossierRef(
        uid=dossier_id,
        titre=title,
        slug=slug,
        an_url="",
        senat_url=senat_url,
        lectures=lectures,
    )
    return dossier


def download_rss(url: str) -> str:
    http_session = get_http_session()
    resp = http_session.get(f"{BASE_URL_SENAT}{url}")
    if resp.status_code != HTTPStatus.OK:
        raise RuntimeError(f"Failed to download RSS url: {url}")

    content: str = resp.text
    return content


_PHASES = {
    "Première lecture": Phase.PREMIERE_LECTURE,
    "Deuxième lecture": Phase.DEUXIEME_LECTURE,
    "Nouvelle lecture": Phase.NOUVELLE_LECTURE,
    "Lecture définitive": Phase.LECTURE_DEFINITIVE,
}


def create_lecture(
    dossier_id: str, entry: element.Tag, prev_texte: Optional[TexteRef] = None
) -> Optional[LectureRef]:
    title = entry.title.string
    if not title.startswith("Texte "):
        return None

    chambre = guess_chambre(entry)
    if chambre != Chambre.SENAT:
        return None

    summary = entry.summary.string
    if re.search(r"Texte (adopté|modifié) par le Sénat", summary):
        return None

    phase = summary.split(" - ", 1)[0]
    texte = create_texte(dossier_id, entry)

    # The logic below might be counter-intuitive, remember that we are checking
    # data from a feed so if the item is related to the texte of a commission,
    # it is the following séance publique related to that texte.
    mo = re.search(r"Texte (résultat des travaux )?de la commission", summary)
    if mo is not None:
        examen = "Séance publique"
        organe = ORGANE_SENAT
        if mo.group(1):
            if prev_texte is None:
                logger.warning("Expected a prev_texte")
                return None
            texte = prev_texte
    else:
        examen = "Commissions"
        organe = ""

    titre = f"{phase} – {examen}"

    return LectureRef(
        chambre=Chambre.SENAT,
        phase=_PHASES.get(phase, Phase.INCONNUE),
        titre=titre,
        organe=organe,
        texte=texte,
    )


def create_texte(dossier_id: str, entry: element.Tag) -> TexteRef:
    numero = entry.title.string.split(" n° ", 1)[1]
    type_dict = {
        "ppr": TypeTexte.PROPOSITION,
        "ppl": TypeTexte.PROPOSITION,
        "pjl": TypeTexte.PROJET,
        "plf": TypeTexte.PROJET,  # plfss
    }
    type_ = dossier_id[:3]
    # One day is added considering we have to deal with timezones
    # and we only need the date.
    # E.g.: 2019-05-21T22:00:00Z
    datetime_depot = datetime.strptime(entry.created.string, "%Y-%m-%dT%H:%M:%SZ")
    date_depot = datetime_depot.date() + timedelta(days=1)
    uid = f"{type_.upper()}SENAT{date_depot.year}X{numero}"
    return TexteRef(
        uid=uid,
        type_=type_dict[type_],
        chambre=Chambre.SENAT,
        legislature=None,
        numero=int(numero),
        titre_long="",
        titre_court="",
        date_depot=date_depot,
    )


def guess_chambre(entry: element.Tag) -> Optional[Chambre]:
    # if "1408" in entry.title.string:
    #     import pdb

    #     pdb.set_trace()
    if entry.id.string.startswith(BASE_URL_SENAT):
        return Chambre.SENAT

    if re.search(r"^http://www2?\.assemblee-nationale\.fr", entry.id.string):
        return Chambre.AN

    if "Texte transmis à l'Assemblée nationale" in entry.summary.string:
        return Chambre.AN

    if entry.summary.string.startswith("Commission mixte paritaire"):
        return None

    # Fallback on Senat given sometimes URLs are relative.
    return Chambre.SENAT
