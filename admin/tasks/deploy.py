from pathlib import Path
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

    hostname = ctx.run("hostname").stdout
    environment = hostname.split(".", 1)[0]

    deploy_id = rollbar_deploy_start(
        ctx, branch, environment, comment=f"[{branch}] {message}"
    )

    try:

        user = "repondeur"
        install_locale(ctx, "fr_FR.utf8")
        create_user(ctx, name=user, home_dir="/srv/repondeur")
        clone_repo(
            ctx,
            repo="https://github.com/betagouv/zam.git",
            branch=branch,
            path="/srv/repondeur/src",
            user=user,
        )
        app_dir = "/srv/repondeur/src/repondeur"
        venv_dir = "/srv/repondeur/venv"

        # Stop workers to free up some system resources during deployment
        ctx.sudo("systemctl stop zam_worker", warn=True)

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
            },
        )
        if wipe:
            wipe_db(ctx, dbname=dbname)
        setup_db(ctx, dbname=dbname, dbuser=dbuser, dbpassword=dbpassword)
        migrate_db(ctx, app_dir=app_dir, venv_dir=venv_dir, user=user)
        setup_webapp_service(ctx)
        setup_worker_service(ctx)
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


@task
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


@task
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
    ctx.sudo("systemctl enable zam_webapp")
    ctx.sudo("systemctl restart zam_webapp")


@task
def setup_worker_service(ctx):
    sudo_put(ctx, "files/zam_worker.service", "/etc/systemd/system/zam_worker.service")
    ctx.sudo("systemctl enable zam_worker")
    ctx.sudo("systemctl restart zam_worker")


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
