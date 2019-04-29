from pathlib import Path
from uuid import uuid4

from commonmark import commonmark
import requests
from fabric.tasks import task

from tools import (
    clone_repo,
    cpu_count,
    create_directory,
    create_postgres_user,
    create_postgres_database,
    create_user,
    install_locale,
    install_packages,
    run_as_postgres,
    sudo_put,
    template_local_file,
    timestamp,
)


# Rollbar token with permissions to post items & deploys
# cf. https://rollbar.com/zam/zam/settings/access_tokens/
ROLLBAR_TOKEN = "8173da84cb344c169bdee21f91e8f529"


@task
def system(ctx):
    ctx.sudo(
        "curl -L -O https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.bionic_amd64.deb"
    )
    install_packages(
        ctx,
        "git",
        "libpq-dev",
        "locales",
        "nginx",
        "postgresql",
        "python3",
        "python3-pip",
        "python3-venv",
        "python3-swiftclient",
        "python3-wheel",
        "redis-server",
        "./wkhtmltox_0.12.5-1.bionic_amd64.deb",
        "xvfb",
    )
    ctx.sudo("mkdir -p /srv/zam")
    ctx.sudo("mkdir -p /srv/zam/letsencrypt/.well-known/acme-challenge")
    create_user(ctx, "zam", "/srv/zam/")
    ctx.sudo("chown zam:users /srv/zam/")
    ctx.sudo("chsh -s /bin/bash zam")


@task
def http(ctx):
    sudo_put(ctx, "letsencrypt.conf", "/etc/nginx/snippets/letsencrypt.conf")
    sudo_put(ctx, "ssl.conf", "/etc/nginx/snippets/ssl.conf")
    certif = f"/etc/letsencrypt/live/{ctx.host}/fullchain.pem"
    exists = ctx.sudo(f'[ -f "{certif}" ]', warn=True)
    if exists.ok:
        with template_local_file(
            "nginx-https.conf.template",
            "nginx-https.conf",
            {"host": ctx.host, "timeout": ctx.config["request_timeout"]},
        ):
            sudo_put(ctx, "nginx-https.conf", "/etc/nginx/sites-available/default")
    else:
        # Before letsencrypt.
        with template_local_file(
            "nginx-http.conf.template", "nginx-http.conf", {"host": ctx.host}
        ):
            sudo_put(ctx, "nginx-http.conf", "/etc/nginx/sites-available/default")
    ctx.sudo("systemctl restart nginx")


@task
def bootstrap(ctx, os_storage_url="", os_auth_token=""):
    system(ctx)
    monitoring(ctx)
    http(ctx)
    letsencrypt(ctx)
    basicauth(ctx)
    # Now put the https ready Nginx conf.
    http(ctx)
    setup_backups(ctx, os_storage_url, os_auth_token)


@task
def basicauth(ctx, user="demozam"):
    install_packages(ctx, "apache2-utils")
    # Will prompt for password.
    ctx.sudo(f"touch /etc/nginx/.htpasswd")
    ctx.sudo(f"htpasswd /etc/nginx/.htpasswd {user}")


@task
def letsencrypt(ctx):
    ctx.sudo("add-apt-repository ppa:certbot/certbot")
    install_packages(ctx, "certbot", "software-properties-common")
    with template_local_file("certbot.ini.template", "certbot.ini", {"host": ctx.host}):
        sudo_put(ctx, "certbot.ini", "/srv/zam/certbot.ini")
    sudo_put(ctx, "ssl-renew", "/etc/cron.weekly/ssl-renew")
    ctx.sudo("chmod +x /etc/cron.weekly/ssl-renew")
    ctx.sudo(
        "certbot certonly -c /srv/zam/certbot.ini --non-interactive --agree-tos"
    )


@task
def sshkeys(ctx):
    for name, key in ctx.config.get("ssh_keys", {}).items():
        ctx.run(
            'grep -q -r "{key}" .ssh/authorized_keys '
            '|| echo "{key}" '
            "| sudo tee --append .ssh/authorized_keys".format(key=key)
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
    rollbar_token=ROLLBAR_TOKEN,
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

    environment = ctx.host.split(".", 1)[0]

    deploy_id = rollbar_deploy_start(
        ctx, rollbar_token, branch, environment, comment=f"[{branch}] {message}"
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
                "rollbar_token": rollbar_token,
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
        rollbar_deploy_update(rollbar_token, deploy_id, status="failed")
    else:
        rollbar_deploy_update(rollbar_token, deploy_id, status="succeeded")


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
def setup_db(ctx, dbname, dbuser, dbpassword, encoding="UTF8", locale="en_US.UTF8"):
    create_postgres_user(ctx, dbuser, dbpassword)
    create_postgres_database(ctx, dbname, dbuser, encoding, locale)


@task
def setup_backups(ctx, os_storage_url="", os_auth_token=""):
    ctx.sudo("python3 -m pip install rotate-backups")
    with template_local_file(
        "cron-zam-backups.sh.template",
        "cron-zam-backups.sh",
        {"os_storage_url": os_storage_url, "os_auth_token": os_auth_token},
    ):
        sudo_put(ctx, "cron-zam-backups.sh", "/etc/cron.hourly/zam-backups")

    ctx.sudo("chmod 755 /etc/cron.hourly/zam-backups")


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
    sudo_put(ctx, "zam_webapp.service", "/etc/systemd/system/zam_webapp.service")
    ctx.sudo("systemctl enable zam_webapp")
    ctx.sudo("systemctl restart zam_webapp")


@task
def setup_worker_service(ctx):
    sudo_put(ctx, "zam_worker.service", "/etc/systemd/system/zam_worker.service")
    ctx.sudo("systemctl enable zam_worker")
    ctx.sudo("systemctl restart zam_worker")


def rollbar_deploy_start(ctx, rollbar_token, branch, environment, comment):
    local_username = ctx.local("whoami").stdout
    revision = ctx.local(f'git log -n 1 --pretty=format:"%H" origin/{branch}').stdout
    resp = requests.post(
        "https://api.rollbar.com/api/1/deploy/",
        {
            "access_token": rollbar_token,
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


@task
def logs_webapp(ctx, lines=100):
    ctx.sudo(f"journalctl --unit zam_webapp.service -n {lines}")


@task
def logs_worker(ctx, lines=100):
    ctx.sudo(f"journalctl --unit zam_worker.service -n {lines}")


@task
def logs_http(ctx, lines=10):
    ctx.sudo(
        " | ".join(
            [
                "cat /var/log/nginx/access.log",
                r"grep -v ' - - \['",  # skip unauthenticated requests
                "grep -v '/check'",  # skip periodic update checks
                f"tail -n {lines}",
            ]
        )
    )


@task
def monitoring(ctx):
    """
    Setup basic system monitoring using munin
    """
    install_packages(
        ctx, "munin", "munin-node", "libdbd-pg-perl", "libparse-http-useragent-perl"
    )
    sudo_put(ctx, "munin/munin.conf", "/etc/munin/munin.conf")
    sudo_put(ctx, "munin/munin-node.conf", "/etc/munin/munin-node.conf")
    _munin_setup_nginx_plugin(ctx)
    _munin_setup_postgres_plugin(ctx)
    _munin_setup_redis_plugin(ctx)
    ctx.sudo("systemctl restart munin-node")


def _munin_setup_nginx_plugin(ctx):
    sudo_put(ctx, "munin/munin-nginx.conf", "/etc/munin/plugin-conf.d/munin-nginx.conf")
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/nginx_request' '/etc/munin/plugins/nginx_request'"
    )
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/nginx_status' '/etc/munin/plugins/nginx_status'"
    )


def _munin_setup_postgres_plugin(ctx):
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/postgres_autovacuum' '/etc/munin/plugins/postgres_autovacuum'"
    )
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/postgres_bgwriter' '/etc/munin/plugins/postgres_bgwriter'"
    )
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/postgres_cache_' '/etc/munin/plugins/postgres_cache_zam'"
    )
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/postgres_checkpoints' '/etc/munin/plugins/postgres_checkpoints'"
    )
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/postgres_connections_' '/etc/munin/plugins/postgres_connections_zam'"
    )
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/postgres_connections_db' '/etc/munin/plugins/postgres_connections_db'"
    )
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/postgres_locks_' '/etc/munin/plugins/postgres_locks_zam'"
    )
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/postgres_querylength_' '/etc/munin/plugins/postgres_querylength_zam'"
    )
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/postgres_scans_' '/etc/munin/plugins/postgres_scans_zam'"
    )
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/postgres_size_' '/etc/munin/plugins/postgres_size_zam'"
    )
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/postgres_transactions_' '/etc/munin/plugins/postgres_transactions_zam'"
    )
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/postgres_tuples_' '/etc/munin/plugins/postgres_tuples_zam'"
    )
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/postgres_users' '/etc/munin/plugins/postgres_users'"
    )
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/postgres_xlog' '/etc/munin/plugins/postgres_xlog'"
    )
    ctx.sudo("rm -f /etc/munin/plugins/postgres_cache_ALL")
    ctx.sudo("rm -f /etc/munin/plugins/postgres_connections_ALL")
    ctx.sudo("rm -f /etc/munin/plugins/postgres_locks_ALL")
    ctx.sudo("rm -f /etc/munin/plugins/postgres_querylength_ALL")
    ctx.sudo("rm -f /etc/munin/plugins/postgres_size_ALL")
    ctx.sudo("rm -f /etc/munin/plugins/postgres_transactions_ALL")


def _munin_setup_redis_plugin(ctx):
    sudo_put(ctx, "munin/munin-redis.sh", "/usr/share/munin/plugins/redis_")
    ctx.sudo("chmod +x /usr/share/munin/plugins/redis_")
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/redis_' '/etc/munin/plugins/redis_127.0.0.1_6379'"
    )
