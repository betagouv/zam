import posixpath
from shlex import quote

from fabric import task

from tasks.system import setup_common
from tools import template_local_file
from tools.command import command
from tools.file import (
    create_directory,
    is_directory,
    is_file,
    sudo_put,
    sudo_put_if_modified,
)
from tools.firewalld import add_services, enable_firewall, start_firewall
from tools.letsencrypt import install_certbot
from tools.munin import (
    add_monitored_node,
    add_munin_repository,
    install_munin,
    munin_graphs_path,
)
from tools.nginx import add_nginx_repository, install_nginx
from tools.package import install_package
from tools.selinux import is_selinux_enabled, set_selinux_bool
from tools.systemd import (
    enable_service,
    is_service_started,
    reload_service,
    start_service,
)


@task
def bootstrap_web(
    ctx,
    hostname="",
    public_name="",
    contact_email=None,
    user="",
    ssl="self-signed",
    app_host_ip="127.0.0.1",
    db_host_ip="127.0.0.1",
    ssl_redir_port="443",
):
    print("\033[95m=== Bootstrapping web server ===\033[0m")

    assert ssl in {"self-signed", "letsencrypt", "custom"}

    if contact_email is None:
        contact_email = ctx.config["contact_email"]

    setup_common(ctx, hostname=hostname)

    enable_firewall(ctx)
    start_firewall(ctx)
    add_services(ctx, "http", "https")  # ports 80 & 443

    setup_nginx(ctx)

    # SELinux may prevent nginx from connecting to the upstream app
    if is_selinux_enabled(ctx):
        set_selinux_bool(ctx, "httpd_can_network_connect", "true")

    extra_config = ""

    if ssl == "self-signed":
        ssl_cert = "/etc/nginx/self-signed.crt"
        ssl_key = "/etc/nginx/self-signed.key"
        if not is_file(ctx, ssl_cert) or not is_file(ctx, ssl_key):
            setup_self_signed_cert(
                ctx, public_name=public_name, ssl_cert=ssl_cert, ssl_key=ssl_key
            )

    elif ssl == "letsencrypt":
        ssl_cert = f"/etc/letsencrypt/live/{public_name}/fullchain.pem"
        ssl_key = f"/etc/letsencrypt/live/{public_name}/privkey.pem"
        extra_config = "include /etc/nginx/snippets/letsencrypt.conf;"
        setup_letsencrypt_cert(ctx, public_name, email=contact_email)

    elif ssl == "custom":
        ssl_cert = "/etc/nginx/zam.crt"  # please supply
        ssl_key = "/etc/nginx/zam.key"  # please supply

    setup_munin_server(ctx, app_host_ip=app_host_ip, db_host_ip=db_host_ip)

    setup_final_nginx_config(
        ctx,
        hostname=public_name,
        ssl_cert=ssl_cert,
        ssl_key=ssl_key,
        ssl_redir_port=ssl_redir_port,
        app_host_ip=app_host_ip,
        extra_config=extra_config,
    )

    if is_service_started(ctx, "nginx"):
        reload_service(ctx, "nginx")
    else:
        start_service(ctx, "nginx")


def setup_nginx(ctx):
    add_nginx_repository(ctx)
    install_nginx(ctx)
    enable_service(ctx, "nginx")


@command
def setup_self_signed_cert(ctx, public_name, ssl_cert, ssl_key):
    """Installing self-signed TLS certificate"""
    ctx.sudo(
        "openssl req -x509 -newkey rsa:4096"
        f" -keyout {quote(ssl_key)}"
        f" -out {quote(ssl_cert)}"
        " -days 365"
        " -sha256"
        " -nodes"
        f" -subj '/C=FR/OU=Zam/CN={public_name}'"
    )


@command
def setup_letsencrypt_cert(ctx, public_name, email):
    install_certbot(ctx)

    www_dir = "/var/www/html/letsencrypt"

    with template_local_file(
        "files/letsencrypt/certbot.ini.template",
        "files/letsencrypt/certbot.ini",
        {"host": public_name, "email": email, "www_dir": www_dir},
    ):
        sudo_put(ctx, "files/letsencrypt/certbot.ini", "/etc/letsencrypt/certbot.ini")

    with template_local_file(
        "files/letsencrypt/letsencrypt.conf.template",
        "files/letsencrypt/letsencrypt.conf",
        {"www_dir": www_dir},
    ):
        if not is_directory(ctx, "/etc/nginx/snippets"):
            create_directory(ctx, "/etc/nginx/snippets", owner="root")

        sudo_put_if_modified(
            ctx,
            "files/letsencrypt/letsencrypt.conf",
            "/etc/nginx/snippets/letsencrypt.conf",
        )

    setup_temporary_nginx_config(ctx, public_name, www_dir)

    if is_service_started(ctx, "nginx"):
        reload_service(ctx, "nginx")
    else:
        start_service(ctx, "nginx")

    # Ask for a certificate
    ctx.sudo(
        "certbot certonly -c /etc/letsencrypt/certbot.ini --non-interactive --agree-tos"
    )

    # Renew certificate every week
    sudo_put(ctx, "files/letsencrypt/ssl-renew", "/etc/cron.weekly/ssl-renew")
    ctx.sudo("chmod +x /etc/cron.weekly/ssl-renew")


@command
def setup_temporary_nginx_config(ctx, hostname, www_dir):
    """Setup temporary Nginx config"""

    challenge_dir = posixpath.join(www_dir, ".well-known/acme-challenge")
    if not is_directory(ctx, challenge_dir):
        create_directory(ctx, challenge_dir, owner="root")

    with template_local_file(
        "files/nginx/http.conf.template", "files/nginx/http.conf", {"host": hostname}
    ):
        sudo_put(ctx, "files/nginx/http.conf", "/etc/nginx/conf.d/zam.conf")


@command
def setup_final_nginx_config(
    ctx, hostname, ssl_cert, ssl_key, ssl_redir_port, app_host_ip, extra_config
):

    if not is_directory(ctx, "/etc/nginx/snippets"):
        create_directory(ctx, "/etc/nginx/snippets", owner="root")

    sudo_put_if_modified(ctx, "files/nginx/ssl.conf", "/etc/nginx/snippets/ssl.conf")

    munin_htpasswd_path = "/etc/nginx/.htpasswd-stats"
    if not is_file(ctx, munin_htpasswd_path):
        install_package(ctx, "httpd-tools")
        ctx.sudo(f"touch {munin_htpasswd_path}")
        ctx.sudo(f"htpasswd {munin_htpasswd_path} stats")  # will prompt for password.

    with template_local_file(
        "files/nginx/https.conf.template",
        "files/nginx/https.conf",
        {
            "host": hostname,
            "timeout": ctx.config["request_timeout"],
            "ssl_cert": ssl_cert,
            "ssl_key": ssl_key,
            "ssl_redir_port": ssl_redir_port,
            "app_host_ip": app_host_ip,
            "munin_graphs_path": munin_graphs_path(ctx),
            "munin_htpasswd_path": munin_htpasswd_path,
            "extra_config": extra_config,
        },
    ):
        sudo_put(ctx, "files/nginx/https.conf", "/etc/nginx/conf.d/zam.conf")


@command
def setup_munin_server(ctx, app_host_ip, db_host_ip):
    """Setup Munin server"""
    add_munin_repository(ctx)
    install_munin(ctx)

    if app_host_ip != "127.0.0.1":
        add_monitored_node(ctx, "app", app_host_ip)

    if db_host_ip != "127.0.0.1":
        add_monitored_node(ctx, "db", db_host_ip)


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
