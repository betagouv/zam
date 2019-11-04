from pathlib import Path
from shlex import quote
from uuid import uuid4

import requests
from commonmark import commonmark
from fabric.tasks import task

from tools import template_local_file
from tools.file import create_directory, is_directory, sudo_put
from tools.git import clone_or_update_repo
from tools.redis import redis_service_name
from tools.run import sudo_in_dir
from tools.system import cpu_count
from tools.systemd import is_service_started, start_service, stop_service

DEFAULT_EMAIL_WHITELIST_PATTERN = "*@*.gouv.fr"

BADGE_COLORS = {"demo": "#b5bd68", "test": "#de935f"}

USER = "zam"
app_dir = "/srv/zam/src/repondeur"
venv_dir = "/srv/zam/venv"


@task
def deploy_changelog(ctx, source="../CHANGELOG.md"):
    content = commonmark(Path(source).read_text())
    with template_local_file("index.html.template", "index.html", {"content": content}):
        sudo_put(ctx, "index.html", "/srv/zam/index.html", chown=USER)


@task
def deploy_app(
    ctx,
    public_name,
    branch="master",
    message="",
    session_secret="",
    auth_secret="",
    listen_address="127.0.0.1",
    db_host_ip="localhost",
    dbname="zam",
    dbuser="zam",
    dbpassword="iloveamendements",
    notify_rollbar=True,
    environment=None,
    http_cache_dir="/var/cache/zam/http",
    uploads_backup_dir="/var/backups/zam/uploads",
):
    print("=== Deploying app ===")

    if not session_secret:
        session_secret = retrieve_secret_from_config(ctx, "session_secret")
    if not session_secret:
        session_secret = uuid4()
        print(f"--- Initializing session_secret to {session_secret} ---")

    if not auth_secret:
        auth_secret = retrieve_secret_from_config(ctx, "auth_secret")
    if not auth_secret:
        auth_secret = uuid4()
        print(f"--- Initializing auth_secret to {auth_secret} ---")

    if environment is None:
        environment = public_name.split(".", 1)[0]
    menu_badge_label = environment[4:] if environment.startswith("zam-") else ""
    menu_badge_color = BADGE_COLORS.get(menu_badge_label, "#999999")

    if notify_rollbar:
        deploy_id = rollbar_deploy_start(
            ctx, branch, environment, comment=f"[{branch}] {message}"
        )

    try:
        print("--- Cloning or updating git repository ---")
        clone_or_update_repo(
            ctx,
            repo="https://github.com/betagouv/zam.git",
            branch=branch,
            parent_dir="/srv/zam",
            name="src",
            user=USER,
        )

        # Stop workers (if running) to free up some system resources during deployment
        if is_service_started(ctx, "zam_worker"):
            stop_service(ctx, "zam_worker")

        print("--- Creating Python venv ---")
        create_virtualenv(ctx, venv_dir=venv_dir, user=USER)

        print("--- Installing Python dependencies ---")
        install_requirements(ctx, app_dir=app_dir, venv_dir=venv_dir, user=USER)

        if not is_directory(ctx, http_cache_dir):
            create_directory(ctx, http_cache_dir, owner=USER)

        if not is_directory(ctx, uploads_backup_dir):
            create_directory(ctx, uploads_backup_dir, owner=USER)

        print("--- Generating app config file ---")
        db_url = f"postgres://{dbuser}:{dbpassword}@{db_host_ip}:5432/{dbname}"
        gunicorn_workers = (cpu_count(ctx) * 2) + 1
        setup_config(
            ctx,
            app_dir=app_dir,
            user=USER,
            context={
                "db_url": db_url,
                "environment": environment,
                "branch": branch,
                "session_secret": session_secret,
                "auth_secret": auth_secret,
                "rollbar_token": ctx.config["rollbar_token"],
                "listen_address": listen_address,
                "gunicorn_workers": gunicorn_workers,
                "gunicorn_timeout": ctx.config["request_timeout"],
                "menu_badge_label": menu_badge_label,
                "menu_badge_color": menu_badge_color,
                "http_cache_dir": http_cache_dir,
                "uploads_backup_dir": uploads_backup_dir,
            },
        )

        # Also stop webapp (if running) to release any locks on the DB
        if is_service_started(ctx, "zam_webapp"):
            stop_service(ctx, "zam_webapp")

        print("--- Applying database migrations ---")
        migrate_db(ctx, app_dir=app_dir, venv_dir=venv_dir)

        # Initialize email whitelist
        if not whitelist_list(ctx):
            print("--- Initializing e-mail whitelist ---")
            whitelist_add(
                ctx,
                pattern=DEFAULT_EMAIL_WHITELIST_PATTERN,
                comment="Default allowed email pattern",
            )

        print("--- Configuring systemd service for web app ---")
        setup_webapp_service(ctx)

        print("--- Configuring systemd service for workers ---")
        setup_worker_service(ctx)

        print("--- Loading data into Redis cache ---")
        reset_data_locks(ctx, app_dir=app_dir, venv_dir=venv_dir, user=USER)
        load_data(ctx, app_dir=app_dir, venv_dir=venv_dir, user=USER)

        # Update dossiers
        update_dossiers(ctx)

        start_service(ctx, "zam_webapp")

        start_service(ctx, "zam_worker")

    except Exception:
        if notify_rollbar:
            rollbar_deploy_update(
                ctx.config["rollbar_token"], deploy_id, status="failed"
            )
    else:
        if notify_rollbar:
            rollbar_deploy_update(
                ctx.config["rollbar_token"], deploy_id, status="succeeded"
            )


def retrieve_secret_from_config(ctx, name):
    secret = ctx.sudo(
        f'grep "zam.{name}" /srv/zam/src/repondeur/production.ini | cut -d" " -f3',  # noqa
        hide=True,
        user="zam",
    ).stdout.strip()
    return secret


def create_virtualenv(ctx, venv_dir, user):
    ctx.sudo(f"python3 -m venv {venv_dir}", user=user)


def install_requirements(ctx, app_dir, venv_dir, user):
    ctx.sudo(f"{venv_dir}/bin/pip install --upgrade pip setuptools", user=user)
    cmd = (
        f"{venv_dir}/bin/pip install "
        "-r requirements.txt "
        "-r requirements-prod.txt "
        "--no-use-pep517 -e ."
    )
    sudo_in_dir(ctx, cmd, directory=app_dir, user=USER)


def setup_config(ctx, app_dir, user, context):
    with template_local_file(
        "../repondeur/production.ini.template", "../repondeur/production.ini", context
    ):
        sudo_put(
            ctx, "../repondeur/production.ini", f"{app_dir}/production.ini", chown=user
        )


@task
def migrate_db(ctx, app_dir, venv_dir):
    create_directory(ctx, "/var/lib/zam", owner=USER)
    cmd = f"{venv_dir}/bin/alembic -c production.ini upgrade head"
    sudo_in_dir(ctx, cmd, directory=app_dir, user=USER)


def setup_webapp_service(ctx):
    with template_local_file(
        "files/zam_webapp.service.template",
        "files/zam_webapp.service",
        {"redis_service": redis_service_name(ctx)},
    ):
        sudo_put(
            ctx,
            "files/zam_webapp.service",
            "/etc/systemd/system/zam_webapp.service",
            chown="root",
        )
    ctx.sudo("systemctl daemon-reload")
    ctx.sudo("systemctl enable zam_webapp.service")


def setup_worker_service(ctx):
    with template_local_file(
        "files/zam_worker.service.template",
        "files/zam_worker.service",
        {"redis_service": redis_service_name(ctx)},
    ):
        sudo_put(
            ctx,
            "files/zam_worker.service",
            "/etc/systemd/system/zam_worker.service",
            chown="root",
        )
    ctx.sudo("systemctl daemon-reload")
    ctx.sudo("systemctl enable zam_worker.service")


def reset_data_locks(ctx, app_dir, venv_dir, user):
    cmd = f"{venv_dir}/bin/zam_reset_data_locks production.ini#repondeur"
    sudo_in_dir(ctx, cmd, directory=app_dir, user=USER)


def load_data(ctx, app_dir, venv_dir, user):
    cmd = f"{venv_dir}/bin/zam_load_data production.ini#repondeur"
    sudo_in_dir(ctx, cmd, directory=app_dir, user=USER)


@task
def update_dossiers(ctx):
    cmd = f"{venv_dir}/bin/zam_update_dossiers production.ini#repondeur"
    ctx.sudo(f'bash -c "cd {app_dir} && {cmd}"', user=USER)


@task
def whitelist_list(ctx):
    cmd = f"{venv_dir}/bin/zam_whitelist production.ini#repondeur list"
    res = sudo_in_dir(ctx, cmd, directory=app_dir, user=USER)
    return res.stdout


@task
def whitelist_add(ctx, pattern, comment=None):
    cmd = f"{venv_dir}/bin/zam_whitelist production.ini#repondeur add {pattern}"
    if comment is not None:
        cmd += " --comment " + quote(comment)
    sudo_in_dir(ctx, cmd, directory=app_dir, user=USER)


@task
def whitelist_remove(ctx, pattern):
    cmd = f"{venv_dir}/bin/zam_whitelist production.ini#repondeur remove {pattern}"
    sudo_in_dir(ctx, cmd, directory=app_dir, user=USER)


@task
def whitelist_check(ctx, email):
    cmd = f"{venv_dir}/bin/zam_whitelist production.ini#repondeur check {email}"
    sudo_in_dir(ctx, cmd, directory=app_dir, user=USER)


@task
def admin_list(ctx, **kwargs):
    cmd = f"{venv_dir}/bin/zam_admin production.ini#repondeur list"
    res = sudo_in_dir(ctx, cmd, directory=app_dir, user=USER, **kwargs)
    return res.stdout


@task
def admin_grant(ctx, email):
    cmd = f"{venv_dir}/bin/zam_admin production.ini#repondeur grant {email}"
    sudo_in_dir(ctx, cmd, directory=app_dir, user=USER)


@task
def admin_revoke(ctx, email):
    cmd = f"{venv_dir}/bin/zam_admin production.ini#repondeur revoke {email}"
    sudo_in_dir(ctx, cmd, directory=app_dir, user=USER)


def rollbar_deploy_start(ctx, branch, environment, comment):
    local_username = ctx.local("whoami").stdout
    revision = ctx.local(f'git log -n 1 --pretty=format:"%H" origin/{branch}').stdout
    resp = requests.post(
        "https://api.rollbar.com/api/1/deploy/",
        {
            "access_token": ctx.config["rollbar_token"],
            "environment": environment,
            "local_username": local_username,
            "revision": revision,
            "status": "started",
            "comment": comment,
        },
        timeout=3,
    )
    if resp.status_code == 200:
        return resp.json()["data"]["deploy_id"]
    else:
        print(f"Error notifying deploy start: {resp.text}")


def rollbar_deploy_update(rollbar_token, deploy_id, status):
    resp = requests.patch(
        f"https://api.rollbar.com/api/1/deploy/{deploy_id}",
        params={"access_token": rollbar_token},
        data={"status": status},
        timeout=3,
    )
    if resp.status_code != 200:
        print(f"Error updating deploy status: {resp.text}")
