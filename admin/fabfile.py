import os
from contextlib import contextmanager
from hashlib import md5
from pathlib import Path
from shlex import quote
from string import Template

import CommonMark
import requests
from invoke import task


# Rollbar token with permissions to post items & deploys
# cf. https://rollbar.com/zam/zam/settings/access_tokens/
ROLLBAR_TOKEN = "8173da84cb344c169bdee21f91e8f529"


class NginxFriendlyTemplate(Template):
    delimiter = "$$"


@contextmanager
def template_local_file(template_filename, output_filename, data):
    with open(template_filename, encoding="utf-8") as template_file:
        template = NginxFriendlyTemplate(template_file.read())
    with open(output_filename, mode="w", encoding="utf-8") as output_file:
        output_file.write(template.substitute(**data))
    yield
    os.remove(output_filename)


def sudo_put(ctx, local, remote, chown=None):
    tmp = str(Path("/tmp") / md5(remote.encode()).hexdigest())
    ctx.put(local, tmp)
    ctx.sudo(f"mv {quote(tmp)} {quote(remote)}")
    if chown:
        ctx.sudo(f"chown {chown}: {quote(remote)}")


def put_dir(ctx, local, remote, chown=None):
    local = Path(local)
    remote = Path(remote)
    for path in local.rglob("*"):
        relative_path = path.relative_to(local)
        if str(relative_path).startswith("."):
            # Avoid pushing hidden files.
            continue
        if path.is_dir():
            ctx.sudo(f"mkdir -p {quote(remote / relative_path)}")
        else:
            sudo_put(ctx, str(path), str(remote / relative_path), chown)


@task
def system(ctx):
    ctx.sudo("apt update")
    ctx.sudo("apt install -y python3.6 nginx wkhtmltopdf xvfb redis-server")
    ctx.sudo("mkdir -p /srv/zam")
    ctx.sudo("mkdir -p /srv/zam/letsencrypt/.well-known/acme-challenge")
    ctx.sudo("useradd -N zam -d /srv/zam/ || exit 0")
    ctx.sudo("chown zam:users /srv/zam/")
    ctx.sudo("chsh -s /bin/bash zam")


@task
def http(ctx):
    sudo_put(ctx, "letsencrypt.conf", "/etc/nginx/snippets/letsencrypt.conf")
    sudo_put(ctx, "ssl.conf", "/etc/nginx/snippets/ssl.conf")
    certif = f"/etc/letsencrypt/live/{ctx.host}/fullchain.pem"
    exists = ctx.run('if [ -f "{}" ]; then echo 1; fi'.format(certif))
    if exists.stdout:
        with template_local_file(
            "nginx-https.conf.template", "nginx-https.conf", {"host": ctx.host}
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
def bootstrap(ctx):
    system(ctx)
    http(ctx)
    letsencrypt(ctx)
    basicauth(ctx)
    # Now put the https ready Nginx conf.
    http(ctx)


@task
def basicauth(ctx):
    ctx.sudo("apt update")
    ctx.sudo("apt install -y apache2-utils")
    # Will prompt for password.
    ctx.sudo("htpasswd -c /etc/nginx/.htpasswd demozam")


@task
def letsencrypt(ctx):
    ctx.sudo("add-apt-repository ppa:certbot/certbot")
    ctx.sudo("apt update")
    ctx.sudo("apt install -y certbot software-properties-common")
    with template_local_file("certbot.ini.template", "certbot.ini", {"host": ctx.host}):
        sudo_put(ctx, "certbot.ini", "/srv/zam/certbot.ini")
    sudo_put(ctx, "ssl-renew", "/etc/cron.weekly/ssl-renew")
    ctx.sudo("chmod +x /etc/cron.weekly/ssl-renew")
    ctx.sudo(
        "certbot certonly -c /srv/zam/certbot.ini --non-interactive " "--agree-tos"
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
    content = CommonMark.commonmark(Path(source).read_text())
    with template_local_file("index.html.template", "index.html", {"content": content}):
        sudo_put(ctx, "index.html", "/srv/zam/index.html", chown="zam")


@task
def deploy_repondeur(
    ctx, secret, rollbar_token=ROLLBAR_TOKEN, branch="master", wipe=False
):
    environment = ctx.host.split(".", 1)[0]
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
    install_requirements(ctx, app_dir=app_dir, user=user)
    setup_config(
        ctx,
        app_dir=app_dir,
        user=user,
        context={
            "environment": environment,
            "branch": branch,
            "secret": secret,
            "rollbar_token": rollbar_token,
        },
    )
    if wipe:
        wipe_db(ctx, user=user)
    migrate_db(ctx, app_dir=app_dir, user=user)
    setup_webapp_service(ctx)
    setup_worker_service(ctx)
    notify_rollbar(ctx, rollbar_token, branch, environment)


@task
def install_locale(ctx, locale_name):
    installed_locales = [
        line.strip() for line in ctx.sudo(f"locale -a", hide=True).stdout.splitlines()
    ]
    if locale_name not in installed_locales:
        ctx.sudo(f"locale-gen {locale_name}")


@task
def create_user(ctx, name, home_dir):
    if ctx.sudo(f"getent passwd {name}", warn=True, hide=True).failed:
        ctx.sudo(f"useradd --system --create-home --home-dir {quote(home_dir)} {name}")


@task
def clone_repo(ctx, repo, branch, path, user):
    if ctx.run(f"test -d {quote(path)}", warn=True, hide=True).failed:
        ctx.sudo(f"git clone --branch={branch} {repo} {quote(path)}", user=user)
    else:
        git = f"git --work-tree={quote(path)} --git-dir={quote(path + '/.git')}"
        ctx.sudo(f"{git} fetch", user=user)
        ctx.sudo(f"{git} checkout {branch}", user=user)
        ctx.sudo(f"{git} reset --hard origin/{branch}", user=user)


@task
def install_requirements(ctx, app_dir, user):
    ctx.sudo("apt-get update")
    ctx.sudo("apt-get install --yes python3-pip")
    ctx.sudo("python3 -m pip install pipenv==2018.05.18")
    ctx.sudo(f'bash -c "cd {app_dir} && pipenv install"', user=user)


@task
def setup_config(ctx, app_dir, user, context):
    with template_local_file(
        "../repondeur/production.ini.template", "../repondeur/production.ini", context
    ):
        sudo_put(
            ctx, "../repondeur/production.ini", f"{app_dir}/production.ini", chown=user
        )


@task
def wipe_db(ctx, user):
    create_directory(ctx, "/var/backups/zam", owner=user)
    ctx.sudo(
        f"cp --backup=numbered /var/lib/zam/repondeur.db /var/backups/zam/repondeur.db",
        user=user,
    )
    ctx.sudo(f"rm -f /var/lib/zam/repondeur.db", user=user)


@task
def migrate_db(ctx, app_dir, user):
    create_directory(ctx, "/var/lib/zam", owner=user)
    ctx.sudo(
        f'bash -c "cd {app_dir} && pipenv run alembic -c production.ini upgrade head"',
        user=user,
    )


@task
def create_directory(ctx, path, owner):
    ctx.sudo(f"mkdir -p {quote(path)}")
    ctx.sudo(f"chown {owner}: {quote(path)}")


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


def notify_rollbar(ctx, rollbar_token, branch, environment):
    local_username = ctx.local("whoami").stdout
    revision = ctx.local(f'git log -n 1 --pretty=format:"%H" origin/{branch}').stdout
    resp = requests.post(
        "https://api.rollbar.com/api/1/deploy/",
        {
            "access_token": rollbar_token,
            "environment": environment,
            "local_username": local_username,
            "revision": revision,
        },
        timeout=3,
    )
    if resp.status_code == 200:
        print("Deploy recorded successfully.")
    else:
        print(f"Error recording deploy: {resp.text}")


@task
def logs_webapp(ctx, lines=100):
    ctx.sudo(f"journalctl --unit zam_webapp.service | tail -n {lines}")


@task
def logs_worker(ctx, lines=100):
    ctx.sudo(f"journalctl --unit zam_worker.service | tail -n {lines}")
