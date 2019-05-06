from fabric.tasks import task

from tools import create_user, debconf, install_packages, sudo_put, template_local_file


@task
def set_hostname(ctx, hostname):
    ctx.sudo(f"hostname {hostname}")
    ctx.sudo(f"echo {hostname} | sudo tee /etc/hostname")


@task
def system(ctx):
    ctx.sudo(
        "curl -L -O https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.bionic_amd64.deb"
    )
    install_packages(
        ctx,
        "git",
        "locales",
        "nginx",
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
    setup_postgres(ctx)
    setup_smtp_server(ctx)
    setup_unattended_upgrades(ctx)


@task
def setup_postgres(ctx):
    install_packages(ctx, "postgresql", "libpq-dev")
    sudo_put(
        ctx,
        "files/postgres.conf",
        "/etc/postgresql/10/main/conf.d/zam.conf",
        chown="postgres",
    )
    ctx.sudo("systemctl reload postgresql@10-main")


@task
def setup_smtp_server(ctx):
    hostname = ctx.run("hostname").stdout.strip()
    debconf(ctx, "postfix", "postfix/main_mailer_type", "string", "Internet Site")
    debconf(ctx, "postfix", "postfix/mailname", "string", hostname)
    install_packages(ctx, "postfix")


@task
def setup_unattended_upgrades(ctx):
    install_packages(ctx, "unattended-upgrades", "bsd-mailx")
    admins = ctx.config.get("admins", [])
    with template_local_file(
        "files/unattended-upgrades.conf.template",
        "files/unattended-upgrades.conf",
        {"email": ",".join(admins)},
    ):
        sudo_put(
            ctx,
            "files/unattended-upgrades.conf",
            "/etc/apt/apt.conf.d/50unattended-upgrades",
        )


@task
def http(ctx):
    sudo_put(
        ctx,
        "files/letsencrypt/letsencrypt.conf",
        "/etc/nginx/snippets/letsencrypt.conf",
    )
    sudo_put(ctx, "files/nginx/ssl.conf", "/etc/nginx/snippets/ssl.conf")
    hostname = ctx.run("hostname").stdout.strip()
    certif = f"/etc/letsencrypt/live/{hostname}/fullchain.pem"
    exists = ctx.sudo(f'[ -f "{certif}" ]', warn=True)
    if exists.ok:
        with template_local_file(
            "files/nginx/https.conf.template",
            "files/nginx/https.conf",
            {"host": hostname, "timeout": ctx.config["request_timeout"]},
        ):
            sudo_put(
                ctx, "files/nginx/https.conf", "/etc/nginx/sites-available/default"
            )
    else:
        # Before letsencrypt.
        with template_local_file(
            "files/nginx/http.conf.template",
            "files/nginx/http.conf",
            {"host": hostname},
        ):
            sudo_put(ctx, "files/nginx/http.conf", "/etc/nginx/sites-available/default")
    ctx.sudo("systemctl restart nginx")


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
    hostname = ctx.run("hostname").stdout.strip()
    with template_local_file(
        "files/letsencrypt/certbot.ini.template",
        "files/letsencrypt/certbot.ini",
        {"host": hostname},
    ):
        sudo_put(ctx, "files/letsencrypt/certbot.ini", "/srv/zam/certbot.ini")
    sudo_put(ctx, "files/letsencrypt/ssl-renew", "/etc/cron.weekly/ssl-renew")
    ctx.sudo("chmod +x /etc/cron.weekly/ssl-renew")
    ctx.sudo("certbot certonly -c /srv/zam/certbot.ini --non-interactive --agree-tos")


@task
def sshkeys(ctx):
    for name, key in ctx.config.get("ssh_keys", {}).items():
        ctx.run(
            'grep -q -r "{key}" .ssh/authorized_keys '
            '|| echo "{key}" '
            "| sudo tee --append .ssh/authorized_keys".format(key=key)
        )
