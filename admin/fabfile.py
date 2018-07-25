import os
from contextlib import contextmanager
from hashlib import md5
from pathlib import Path
from shlex import quote
from string import Template

import CommonMark
from invoke import task


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
    ctx.sudo("apt install -y python3.6 nginx wkhtmltopdf xvfb")
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
def deploy_repondeur(ctx, secret, branch="master", wipe=False):
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
    setup_config(ctx, app_dir=app_dir, user=user, secret=secret)
    if wipe:
        wipe_db(ctx, user=user)
    migrate_db(ctx, app_dir=app_dir, user=user)
    fetch_an_group_data(ctx, user=user)
    setup_service(ctx)


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
def setup_config(ctx, app_dir, user, secret):
    with template_local_file(
        "../repondeur/production.ini.template",
        "../repondeur/production.ini",
        {"secret": secret},
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
    res = ctx.sudo(
        f'bash -c "cd {app_dir} && pipenv run alembic -c production.ini current"',
        user=user,
    )
    current = res.stdout
    action = "upgrade" if current else "stamp"
    ctx.sudo(
        f'bash -c "cd {app_dir} && pipenv run alembic -c production.ini {action} head"',
        user=user,
    )


@task
def fetch_an_group_data(ctx, user):
    url = "http://data.assemblee-nationale.fr/static/openData/repository/15/amo/deputes_actifs_mandats_actifs_organes_divises/AMO40_deputes_actifs_mandats_actifs_organes_divises_XV.json.zip"  # noqa
    filename = "/tmp/groups.zip"
    ctx.sudo(f"curl --silent --show-error {url} -o {filename}", user=user)

    data_dir = "/var/lib/zam/data/an/groups"
    create_directory(ctx, data_dir, owner=user)

    ctx.sudo("apt-get update")
    ctx.sudo("apt-get install --yes unzip")
    ctx.sudo(f"unzip -q -o {filename} -d {data_dir}/", user=user)

    ctx.sudo(f"rm {filename}", user=user)


@task
def create_directory(ctx, path, owner):
    ctx.sudo(f"mkdir -p {quote(path)}")
    ctx.sudo(f"chown {owner}: {quote(path)}")


@task
def setup_service(ctx):
    sudo_put(ctx, "repondeur.service", "/etc/systemd/system/repondeur.service")
    ctx.sudo("systemctl enable repondeur")
    ctx.sudo("systemctl restart repondeur")


@task
def logs(ctx, lines=100):
    ctx.sudo(f"journalctl --unit repondeur.service | tail -n {lines}")
