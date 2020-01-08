from fabric.tasks import task

from tools import template_local_file
from tools.command import command
from tools.file import append, sed, sudo_put
from tools.firewalld import install_firewall
from tools.munin import (
    add_munin_repository,
    install_munin_node,
    munin_node_service_name,
)
from tools.ntp import install_ntp, ntp_service_name
from tools.package import (
    install_package,
    install_packages,
    install_package_updates,
    update_package_cache,
)
from tools.system import SystemSpecificCommand
from tools.systemd import (
    enable_service,
    is_service_started,
    restart_service,
    start_service,
)


def setup_common(ctx, hostname="", munin_server_ip=None):
    if hostname:
        set_hostname(ctx, hostname)
    install_updates(ctx)
    install_firewall(ctx)
    setup_unattended_security_upgrades(ctx, admins=ctx.config.get("admins", []))
    setup_ntp(ctx)
    setup_munin_node(ctx, munin_server_ip=munin_server_ip)


def set_hostname(ctx, hostname):
    ctx.sudo(f"hostname {hostname}")
    ctx.sudo(f"echo {hostname} | sudo tee /etc/hostname", hide=True)


@command
def install_updates(ctx):
    """Install package updates"""
    update_package_cache(ctx)
    install_package_updates(ctx)


class SetupUnattendedSecurityUpgrades(SystemSpecificCommand):
    def debian(self, ctx, admins):
        install_packages(ctx, "unattended-upgrades", "bsd-mailx")
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

    def redhat(self, ctx, admins):
        install_package(ctx, "yum-cron")
        sed(
            ctx,
            filename="/etc/yum/yum-cron.conf",
            match=r"^update_cmd\s*=.*$",
            replace="update_cmd = security",
        )
        sed(
            ctx,
            filename="/etc/yum/yum-cron.conf",
            match=r"^apply_updates\s*=.*$",
            replace="apply_updates = yes",
        )
        email_to = ",".join(admins)
        sed(
            ctx,
            filename="/etc/yum/yum-cron.conf",
            match=r"^email_to\s*=.*$",
            replace=f"apply_updates = {email_to}",
        )
        enable_service(ctx, "yum-cron")
        restart_service(ctx, "yum-cron")


setup_unattended_security_upgrades = SetupUnattendedSecurityUpgrades()


def setup_ntp(ctx):
    install_ntp(ctx)

    service_name = ntp_service_name(ctx)
    enable_service(ctx, service_name)
    start_service(ctx, service_name)


@command
def setup_munin_node(ctx, munin_server_ip=None):
    """Setup Munin node"""
    add_munin_repository(ctx)
    install_munin_node(ctx)
    changed = False
    if munin_server_ip is not None:
        for line in [
            "allow ^" + munin_server_ip.replace(".", r"\.") + "$",
            "allow ^::ffff::" + munin_server_ip.replace(".", r"\.") + "$",
        ]:
            changed |= append(ctx, filename="/etc/munin/munin-node.conf", line=line)
    service_name = munin_node_service_name(ctx)
    enable_service(ctx, service_name)
    if changed or not is_service_started(ctx, service_name):
        restart_service(ctx, service_name)


@task
def sshkeys(ctx):
    for name, key in ctx.config.get("ssh_keys", {}).items():
        ctx.run(
            'grep -q -r "{key}" .ssh/authorized_keys '
            '|| echo "{key}" '
            "| sudo tee --append .ssh/authorized_keys".format(key=key)
        )
