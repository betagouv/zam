from datetime import datetime
from pathlib import Path
import os

from .decorators import require_env_vars


def strip_styles(content: str) -> str:
    return content.replace(' style="text-align:justify;"', "")


@require_env_vars(env_vars=["ZAM_OUTPUT"])
def build_output_filename() -> Path:
    output_root_path = Path(os.environ["ZAM_OUTPUT"])
    current_branch = os.popen("git symbolic-ref --short HEAD").read().strip()
    if current_branch == "master":
        return output_root_path / "index.html"
    now = datetime.utcnow()
    output_dir = f'{now.isoformat()[:len("YYYY-MM-DD")]}-{current_branch}'
    output_path = output_root_path / output_dir
    output_path.mkdir(exist_ok=True)
    return output_path / "index.html"
