from datetime import datetime
from pathlib import Path
import subprocess


def strip_styles(content: str) -> str:
    return content.replace(' style="text-align:justify;"', "")


def build_output_filename(output_folder: str) -> Path:
    output_root_path = Path(output_folder)
    current_branch = get_current_branch()
    if current_branch == "master":
        return output_root_path / "index.html"
    now = datetime.utcnow()
    output_dir = f'{now.isoformat()[:len("YYYY-MM-DD")]}-{current_branch}'
    output_path = output_root_path / output_dir
    output_path.mkdir(exist_ok=True)
    return output_path / "index.html"


def get_current_branch() -> str:
    res = subprocess.run(
        "git symbolic-ref --short HEAD",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        encoding="ascii",
    )
    if res.returncode != 0:
        return "master"
    return res.stdout.strip()
