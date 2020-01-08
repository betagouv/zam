from fabric import task

from tasks.system import setup_common
from tools.command import command
from tools.file import sudo_put
from tools.firewalld import (
    add_service,
    enable_firewall,
    add_port,
    remove_port,
    start_firewall,
)
from tools.locale import install_locale
from tools.munin import enable_munin_plugin
from tools.package import install_packages, is_package_installed
from tools.python import add_python_repository, install_python
from tools.redis import add_redis_repository, install_redis, redis_service_name
from tools.system import SystemSpecificCommand
from tools.systemd import enable_service, start_service
from tools.user import create_user, user_exists


@task
def bootstrap_app(ctx, hostname="", web_host_ip=None, firewall_zone="public"):
    print("\033[95m=== Bootstrapping app server ===\033[0m")
    setup_common(ctx, hostname=hostname, munin_server_ip=web_host_ip)

    enable_firewall(ctx)
    start_firewall(ctx)
    add_service(ctx, "munin-node", zone=firewall_zone)  # port 4949
    if firewall_zone != "public":
        remove_port(ctx, 6543, zone="public")
    add_port(ctx, 6543, zone=firewall_zone)  # zam webapp

    setup_dedicated_user(ctx)
    setup_git(ctx)
    setup_python(ctx)
    install_build_tools(ctx)
    setup_wkhtmltopdf(ctx)
    setup_french_locale(ctx)
    setup_redis(ctx)
    setup_smtp_server(ctx)
    setup_monitoring(ctx)


def setup_dedicated_user(ctx):
    if not user_exists(ctx, name="zam"):
        create_user(ctx, name="zam", home_dir="/srv/zam")


@command
def setup_git(ctx):
    """Install git"""
    if not is_package_installed(ctx, "git"):
        install_packages(ctx, "git")


def setup_python(ctx):
    add_python_repository(ctx)
    install_python(ctx)


class InstallBuildTools(SystemSpecificCommand):
    """Install build tools"""

    def debian(self, ctx):
        if not is_package_installed(ctx, "build-essentials"):
            install_packages(ctx, "build-essentials")
        if not is_package_installed(ctx, "python3-dev"):
            install_packages(ctx, "python3-dev")

    def redhat(self, ctx):
        if not is_package_installed(ctx, "gcc"):
            install_packages(ctx, "gcc")
        if not is_package_installed(ctx, "python3-devel"):
            install_packages(ctx, "python3-devel")


install_build_tools = InstallBuildTools()


def setup_wkhtmltopdf(ctx):
    if not is_package_installed(ctx, "wkhtmltox"):
        install_wkhtmltopdf(ctx)


class InstallWkHTMLToPDF(SystemSpecificCommand):
    """Install wkhtmltopdf"""

    def debian(self, ctx):
        ctx.sudo(
            "curl -L -O https://github.com/wkhtmltopdf/wkhtmltopdf/releases/"
            "download/0.12.5/wkhtmltox_0.12.5-1.bionic_amd64.deb"
        )
        install_packages(ctx, "./wkhtmltox_0.12.5-1.bionic_amd64.deb", "xvfb")

    def redhat(self, ctx):
        ctx.sudo(
            "curl -L -O https://github.com/wkhtmltopdf/wkhtmltopdf/releases/"
            "download/0.12.5/wkhtmltox-0.12.5-1.centos7.x86_64.rpm"
        )
        install_packages(
            ctx, "./wkhtmltox-0.12.5-1.centos7.x86_64.rpm", "xorg-x11-server-Xvfb"
        )


install_wkhtmltopdf = InstallWkHTMLToPDF()


def setup_french_locale(ctx):
    """Needed by tlfp"""
    install_locale(ctx, "fr_FR.utf8")


def setup_redis(ctx):
    add_redis_repository(ctx)
    install_redis(ctx)
    service_name = redis_service_name(ctx)
    enable_service(ctx, service_name)
    start_service(ctx, service_name)


@command
def setup_smtp_server(ctx):
    print("Install SMTP server")
    if not is_package_installed(ctx, "postfix"):
        install_packages(ctx, "postfix")


@command
def setup_monitoring(ctx):
    """Setup monitoring"""
    _setup_munin_redis_plugin(ctx)


def _setup_munin_redis_plugin(ctx):
    sudo_put(ctx, "files/munin/munin-redis.sh", "/usr/share/munin/plugins/redis_")
    ctx.sudo("chmod +x /usr/share/munin/plugins/redis_")
    enable_munin_plugin(ctx, "redis_", "redis_127.0.0.1_6379")


@task
def logs_webapp(ctx, lines=100):
    ctx.sudo(f"journalctl --unit zam_webapp.service -n {lines}")


@task
def logs_worker(ctx, lines=100):
    ctx.sudo(f"journalctl --unit zam_worker.service -n {lines}")
