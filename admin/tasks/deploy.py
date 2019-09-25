from pathlib import Path
from shlex import quote
from uuid import uuid4

import requests
from commonmark import commonmark
from fabric.tasks import task

from tools import (
    clone_repo,
    cpu_count,
    create_directory,
    create_postgres_user,
    create_postgres_database,
    create_user,
    install_locale,
    run_as_postgres,
    sudo_put,
    template_local_file,
    timestamp,
)


DEFAULT_EMAIL_WHITELIST_PATTERN = "*@*.gouv.fr"

BADGE_COLORS = {"demo": "#b5bd68", "test": "#de935f"}

app_dir = "/srv/repondeur/src/repondeur"
venv_dir = "/srv/repondeur/venv"
user = "repondeur"


@task
def deploy_changelog(ctx, source="../CHANGELOG.md"):
    content = commonmark(Path(source).read_text())
    with template_local_file("index.html.template", "index.html", {"content": content}):
        sudo_put(ctx, "index.html", "/srv/zam/index.html", chown="zam")


@task
def deploy_repondeur(
    ctx,
    branch="master",
    message="",
    session_secret="",
    auth_secret="",
    wipe=False,
    dbname="zam",
    dbuser="zam",
    dbpassword="iloveamendements",
):
    if not session_secret:
        session_secret = retrieve_secret_from_config(ctx, "session_secret")
    if not session_secret:
        session_secret = uuid4()
        print(f"Initializing session_secret to {session_secret}")

    if not auth_secret:
        auth_secret = retrieve_secret_from_config(ctx, "auth_secret")
    if not auth_secret:
        auth_secret = uuid4()
        print(f"Initializing auth_secret to {auth_secret}")

    hostname = ctx.run("hostname").stdout.strip()
    environment = hostname.split(".", 1)[0]
    menu_badge_label = environment[4:] if environment.startswith("zam-") else ""
    menu_badge_color = BADGE_COLORS.get(menu_badge_label, "#999999")

    deploy_id = rollbar_deploy_start(
        ctx, branch, environment, comment=f"[{branch}] {message}"
    )

    try:
        install_locale(ctx, "fr_FR.utf8")
        create_user(ctx, name=user, home_dir="/srv/repondeur")
        clone_repo(
            ctx,
            repo="https://github.com/betagouv/zam.git",
            branch=branch,
            path="/srv/repondeur/src",
            user=user,
        )

        # Stop workers (if running) to free up some system resources during deployment
        stop_worker_service(ctx, warn=True)

        create_virtualenv(ctx, venv_dir=venv_dir, user=user)
        install_requirements(ctx, app_dir=app_dir, venv_dir=venv_dir, user=user)
        gunicorn_workers = (cpu_count(ctx) * 2) + 1
        setup_config(
            ctx,
            app_dir=app_dir,
            user=user,
            context={
                "db_url": f"postgres://{dbuser}:{dbpassword}@localhost:5432/{dbname}",
                "environment": environment,
                "branch": branch,
                "session_secret": session_secret,
                "auth_secret": auth_secret,
                "rollbar_token": ctx.config["rollbar_token"],
                "gunicorn_workers": gunicorn_workers,
                "gunicorn_timeout": ctx.config["request_timeout"],
                "menu_badge_label": menu_badge_label,
                "menu_badge_color": menu_badge_color,
            },
        )

        # Also stop webapp (if running) to release any locks on the DB
        stop_webapp_service(ctx, warn=True)

        if wipe:
            wipe_db(ctx, dbname=dbname)
        setup_db(ctx, dbname=dbname, dbuser=dbuser, dbpassword=dbpassword)
        migrate_db(ctx, app_dir=app_dir, venv_dir=venv_dir, user=user)

        # Initialize email whitelist
        if not whitelist_list(ctx):
            whitelist_add(
                ctx,
                pattern=DEFAULT_EMAIL_WHITELIST_PATTERN,
                comment="Default allowed email pattern",
            )

        setup_webapp_service(ctx)
        setup_worker_service(ctx)

        # Load data into Redis cache
        reset_data_locks(ctx, app_dir=app_dir, venv_dir=venv_dir, user=user)
        load_data(ctx, app_dir=app_dir, venv_dir=venv_dir, user=user)

        # Start webapp and workers again
        start_webapp_service(ctx)
        start_worker_service(ctx)

    except Exception as exc:
        rollbar_deploy_update(ctx.config["rollbar_token"], deploy_id, status="failed")
    else:
        rollbar_deploy_update(
            ctx.config["rollbar_token"], deploy_id, status="succeeded"
        )


def retrieve_secret_from_config(ctx, name):
    secret = ctx.run(
        f'grep "zam.{name}" /srv/repondeur/src/repondeur/production.ini | cut -d" " -f3',  # noqa
        hide=True,
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
    ctx.sudo(f'bash -c "cd {app_dir} && {cmd}"', user=user)


def setup_config(ctx, app_dir, user, context):
    with template_local_file(
        "../repondeur/production.ini.template", "../repondeur/production.ini", context
    ):
        sudo_put(
            ctx, "../repondeur/production.ini", f"{app_dir}/production.ini", chown=user
        )


@task
def wipe_db(ctx, dbname):
    backup_db(ctx, dbname)
    # Will be restarted later in `deploy_repondeur`.
    ctx.sudo("systemctl stop zam_webapp")
    ctx.sudo("systemctl stop zam_worker")
    run_as_postgres(ctx, f"dropdb {dbname}")


@task
def backup_db(ctx, dbname="zam"):
    create_directory(ctx, "/var/backups/zam", owner="postgres")
    backup_filename = f"/var/backups/zam/postgres-dump-{timestamp()}.sql"
    run_as_postgres(
        ctx,
        f"pg_dump --dbname={dbname} --create --encoding=UTF8 --file={backup_filename}",
    )


@task
def setup_db(ctx, dbname, dbuser, dbpassword, encoding="UTF8", locale="en_US.UTF8"):
    create_postgres_user(ctx, dbuser, dbpassword)
    create_postgres_database(ctx, dbname, dbuser, encoding, locale)


@task
def migrate_db(ctx, app_dir, venv_dir, user):
    create_directory(ctx, "/var/lib/zam", owner=user)
    cmd = f"{venv_dir}/bin/alembic -c production.ini upgrade head"
    ctx.sudo(f'bash -c "cd {app_dir} && {cmd}"', user=user)


def setup_webapp_service(ctx):
    # Clean up old service
    ctx.sudo(
        " && ".join(
            [
                "[ -f /etc/systemd/system/repondeur.service ]",
                "systemctl stop repondeur",
                "systemctl disable repondeur",
                "rm -f /etc/systemd/system/repondeur.service",
            ]
        )
        + " || exit 0"
    )
    sudo_put(ctx, "files/zam_webapp.service", "/etc/systemd/system/zam_webapp.service")
    ctx.sudo("systemctl daemon-reload")
    ctx.sudo("systemctl enable zam_webapp")


def start_webapp_service(ctx):
    ctx.sudo("systemctl start zam_webapp")


def stop_webapp_service(ctx, warn=False):
    ctx.sudo("systemctl stop zam_webapp", warn=warn)


def restart_webapp_service(ctx):
    ctx.sudo("systemctl restart zam_webapp")


def setup_worker_service(ctx):
    sudo_put(ctx, "files/zam_worker.service", "/etc/systemd/system/zam_worker.service")
    ctx.sudo("systemctl daemon-reload")
    ctx.sudo("systemctl enable zam_worker")


def start_worker_service(ctx):
    ctx.sudo("systemctl start zam_worker")


def stop_worker_service(ctx, warn=False):
    ctx.sudo("systemctl stop zam_worker", warn=warn)


def restart_worker_service(ctx):
    ctx.sudo("systemctl restart zam_worker")


def reset_data_locks(ctx, app_dir, venv_dir, user):
    cmd = f"{venv_dir}/bin/zam_reset_data_locks production.ini#repondeur"
    ctx.sudo(f'bash -c "cd {app_dir} && {cmd}"', user=user)


def load_data(ctx, app_dir, venv_dir, user):
    cmd = f"{venv_dir}/bin/zam_load_data production.ini#repondeur"
    ctx.sudo(f'bash -c "cd {app_dir} && {cmd}"', user=user)


@task
def whitelist_list(ctx):
    cmd = f"{venv_dir}/bin/zam_whitelist production.ini#repondeur list"
    res = ctx.sudo(f'bash -c "cd {app_dir} && {cmd}"', user=user)
    return res.stdout


@task
def whitelist_add(ctx, pattern, comment=None):
    cmd = f"{venv_dir}/bin/zam_whitelist production.ini#repondeur add {pattern}"
    if comment is not None:
        cmd += " --comment " + quote(comment)
    ctx.sudo(f'bash -c "cd {app_dir} && {cmd}"', user=user)


@task
def whitelist_remove(ctx, pattern):
    cmd = f"{venv_dir}/bin/zam_whitelist production.ini#repondeur remove {pattern}"
    ctx.sudo(f'bash -c "cd {app_dir} && {cmd}"', user=user)


@task
def whitelist_check(ctx, email):
    cmd = f"{venv_dir}/bin/zam_whitelist production.ini#repondeur check {email}"
    ctx.sudo(f'bash -c "cd {app_dir} && {cmd}"', user=user)


@task
def admin_list(ctx):
    cmd = f"{venv_dir}/bin/zam_admin production.ini#repondeur list"
    res = ctx.sudo(f'bash -c "cd {app_dir} && {cmd}"', user=user)
    return res.stdout


@task
def admin_grant(ctx, email):
    cmd = f"{venv_dir}/bin/zam_admin production.ini#repondeur grant {email}"
    ctx.sudo(f'bash -c "cd {app_dir} && {cmd}"', user=user)


@task
def admin_revoke(ctx, email):
    cmd = f"{venv_dir}/bin/zam_admin production.ini#repondeur revoke {email}"
    ctx.sudo(f'bash -c "cd {app_dir} && {cmd}"', user=user)


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
