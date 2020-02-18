from datetime import date, datetime
from itertools import groupby
from typing import TYPE_CHECKING, Iterable, List, Optional, Tuple

import pytz
from jinja2 import Markup

# Make these types available to mypy, but avoid circular imports
if TYPE_CHECKING:
    from zam_repondeur.models import Amendement, Article, Lecture  # noqa
    from zam_repondeur.models.events.base import Event  # noqa


def paragriphy(content: Optional[str]) -> Markup:
    if content is None:
        content = ""
    if not content.startswith("<p>"):
        content = f"<p>{content}</p>"
    return Markup(content)


def group_by_day(events: List["Event"]) -> List[Tuple[date, List["Event"]]]:
    def by_day(event: "Event") -> date:
        event_date: date = event.created_at.date()
        return event_date

    # We need to explicitly turn it into a list otherwise jinja2 is lost.
    return [(key, list(group)) for key, group in groupby(events, key=by_day)]


def h3_to_h5(content: Optional[str]) -> str:
    if content is None:
        return ""
    return content.replace("<h3>", "<h5>").replace("</h3>", "</h5>")


def enumeration(items: List[str]) -> str:
    str_items = [str(item) for item in items]
    if len(str_items) == 0:
        return ""
    if len(str_items) == 1:
        return str_items[0]
    return ", ".join(str_items[:-1]) + " et " + str_items[-1]


def length_including_batches(amendements: Iterable["Amendement"]) -> int:
    return sum(
        len(amdt.location.batch.amendements) if amdt.location.batch else 1
        for amdt in amendements
    )


def human_readable_time(dt: datetime) -> str:
    return _local_time(dt).strftime("%Hh%M")


def human_readable_date_and_time(dt: datetime) -> str:
    return _local_time(dt).strftime("%A %d %B %Y à %H:%M:%S")


def _local_time(dt: datetime) -> datetime:
    local_tz = pytz.timezone("Europe/Paris")
    return dt.astimezone(local_tz)


def number(n: int) -> str:
    return "{:,}".format(n).replace(",", "\u202f")  # narrow non-breaking space
