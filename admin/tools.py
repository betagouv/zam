import os
from contextlib import contextmanager
from datetime import datetime
from hashlib import md5
from pathlib import Path
from shlex import quote
from string import Template

from pytz import UTC


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


def create_directory(ctx, path, owner):
    ctx.sudo(f"mkdir -p {quote(path)}")
    ctx.sudo(f"chown {owner}: {quote(path)}")


def create_user(ctx, name, home_dir):
    if ctx.sudo(f"getent passwd {name}", warn=True, hide=True).failed:
        ctx.sudo(f"useradd --system --create-home --home-dir {quote(home_dir)} {name}")


def clone_repo(ctx, repo, branch, path, user):
    if ctx.run(f"test -d {quote(path)}", warn=True, hide=True).failed:
        ctx.sudo(f"git clone --branch={branch} {repo} {quote(path)}", user=user)
    else:
        git = f"git --work-tree={quote(path)} --git-dir={quote(path + '/.git')}"
        ctx.sudo(f"{git} fetch", user=user)
        ctx.sudo(f"{git} checkout {branch}", user=user)
        ctx.sudo(f"{git} reset --hard origin/{branch}", user=user)


def install_locale(ctx, locale_name):
    installed_locales = [
        line.strip() for line in ctx.sudo(f"locale -a", hide=True).stdout.splitlines()
    ]
    if locale_name not in installed_locales:
        ctx.sudo(f"locale-gen {locale_name}")


def create_postgres_user(ctx, dbuser, dbpassword):
    sql = f"CREATE USER {dbuser} ENCRYPTED PASSWORD '{dbpassword}';"
    run_as_postgres(ctx, f'psql -c "{sql}" || exit 0')


def create_postgres_database(ctx, dbname, owner, encoding, locale):
    run_as_postgres(
        ctx,
        (
            f"createdb --owner={owner} --template=template0 --encoding={encoding} "
            f"--lc-ctype={locale} --lc-collate={locale} {dbname} || exit 0"
        ),
    )


def run_as_postgres(ctx, cmd):
    return ctx.run(f"sudo -Hiu postgres {cmd}")


def timestamp():
    return UTC.localize(datetime.utcnow()).isoformat(timespec="seconds")


def cpu_count(ctx):
    return int(ctx.run("cat /proc/cpuinfo | grep Processor | wc -l").stdout.strip())


def install_packages(ctx, *names):
    ctx.sudo("apt-get update")
    ctx.sudo("apt-get install --yes {}".format(" ".join(names)))
