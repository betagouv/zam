from http import HTTPStatus
from typing import Dict, Set

import requests
from bs4 import BeautifulSoup

from zam_repondeur.fetch.an.dossiers.models import DossierRef, DossierRefsByUID


BASE_URL_SENAT = "http://www.senat.fr"
TEXTES_RECENTS_URL = f"{BASE_URL_SENAT}/dossiers-legislatifs/textes-recents.html"


def get_dossiers_senat() -> DossierRefsByUID:
    html = download_textes_recents()
    webpages_urls = extract_recent_urls(html)
    pids_rss = convert_to_rss_urls(webpages_urls)
    dossier_refs_by_uid = {
        pid: create_dossier(pid, rss_url) for pid, rss_url in pids_rss.items()
    }
    return dossier_refs_by_uid


def download_textes_recents() -> str:
    resp = requests.get(TEXTES_RECENTS_URL)
    if resp.status_code != HTTPStatus.OK:
        raise RuntimeError("Failed to download textes recents from senat.fr")

    return resp.text


def extract_recent_urls(html: str) -> Set[str]:
    soup = BeautifulSoup(html, "html5lib")
    next_textes_box = soup.select(".box.box-type-02")[0]
    return {
        link.attrs.get("href", "")
        for link in next_textes_box.select("a")
        if "/dossier-legislatif/" in link.attrs.get("href", "")
    }


def convert_to_rss_urls(webpages_urls: Set[str]) -> Dict[str, str]:
    pids_rss = {}
    for webpage_url in webpages_urls:
        prefix = len("/dossier-legislatif/")
        suffix = len(".html")
        pid = webpage_url[prefix:-suffix]
        pids_rss[pid] = f"/dossier-legislatif/rss/dosleg{pid}.xml"
    return pids_rss


def create_dossier(pid: str, rss_url: str) -> DossierRef:
    rss_content = download_rss(rss_url)
    soup = BeautifulSoup(rss_content, "html5lib")
    prefix = len("Sénat - ")
    title = soup.title.string[prefix:]
    dossier = DossierRef(uid=pid, titre=title, lectures=[])
    return dossier


def download_rss(url: str) -> str:
    resp = requests.get(f"{BASE_URL_SENAT}{url}")
    if resp.status_code != HTTPStatus.OK:
        raise RuntimeError(f"Failed to download RSS url: {url}")

    return resp.text
