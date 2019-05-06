from fabric.tasks import task

from tools import create_user, install_packages, sudo_put, template_local_file


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
    ctx.sudo("certbot certonly -c /srv/zam/certbot.ini --non-interactive --agree-tos")


@task
def sshkeys(ctx):
    for name, key in ctx.config.get("ssh_keys", {}).items():
        ctx.run(
            'grep -q -r "{key}" .ssh/authorized_keys '
            '|| echo "{key}" '
            "| sudo tee --append .ssh/authorized_keys".format(key=key)
        )
