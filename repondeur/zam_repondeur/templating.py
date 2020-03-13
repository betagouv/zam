from typing import Any, Dict, Optional

from pyramid.config import Configurator
from pyramid.events import BeforeRender
from pyramid.registry import Registry
from pyramid.threadlocal import get_current_registry
from pyramid_jinja2 import Environment, IJinja2Environment

FILTERS_PATH = "zam_repondeur.views.jinja2_filters"

JINJA2_SETTINGS = {
    "jinja2.filters": {
        "paragriphy": f"{FILTERS_PATH}:paragriphy",
        "group_by_day": f"{FILTERS_PATH}:group_by_day",
        "h3_to_h5": f"{FILTERS_PATH}:h3_to_h5",
        "enumeration": f"{FILTERS_PATH}:enumeration",
        "length_including_batches": f"{FILTERS_PATH}:length_including_batches",
        "human_readable_time": f"{FILTERS_PATH}:human_readable_time",
        "human_readable_date_and_time": f"{FILTERS_PATH}:human_readable_date_and_time",
        "number": f"{FILTERS_PATH}:number",
    },
    "jinja2.undefined": "strict",
    "jinja2.trim_blocks": "true",
    "jinja2.lstrip_blocks": "true",
}


def includeme(config: Configurator) -> None:
    config.add_settings(JINJA2_SETTINGS)
    config.include("pyramid_jinja2")
    config.add_jinja2_renderer(".html")
    config.add_jinja2_search_path("zam_repondeur:templates", name=".html")
    config.add_subscriber(add_renderer_globals, BeforeRender)


def add_renderer_globals(event: BeforeRender) -> None:
    registry = get_current_registry()
    event["app_name"] = registry.settings["zam.app_name"]
    event["contact_email"] = registry.settings["zam.contact_email"]


def render_template(
    name: str, context: Dict[str, Any], registry: Optional[Registry] = None
) -> str:
    env = get_jinja2_environment(registry)
    template = env.get_template(name)
    content: str = template.render(**context)
    return content


def get_jinja2_environment(registry: Optional[Registry] = None) -> Environment:
    if registry is None:
        registry = get_current_registry()
    env: Optional[Environment] = registry.queryUtility(IJinja2Environment, name=".html")
    if env is None:
        raise RuntimeError("No Jinja2 environment configured")
    return env
