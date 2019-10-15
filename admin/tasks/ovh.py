from fabric import task
from fabric.connection import Connection

from tools import template_local_file
from tools.firewalld import remove_services, set_interface_zone
from tools.file import sudo_put_if_modified

from .app import bootstrap_app
from .db import bootstrap_db
from .deploy import deploy_app
from .web import bootstrap_web


@task
def bootstrap_ovh(
    ctx,
    public_name,
    public_web_ip,
    private_web_ip,
    public_app_ip,
    private_app_ip,
    public_db_ip,
    private_db_ip,
    environment="zam-sec",
    branch="master",
    contact_email=None,
):
    _bootstrap_ovh_web(
        Connection(host=f"centos@{public_web_ip}", config=ctx.config),
        public_name=public_name,
        private_web_ip=private_web_ip,
        private_app_ip=private_app_ip,
        private_db_ip=private_db_ip,
        contact_email=contact_email,
    )
    _bootstrap_ovh_db(
        Connection(host=f"centos@{public_db_ip}", config=ctx.config),
        private_web_ip=private_web_ip,
        private_app_ip=private_app_ip,
        private_db_ip=private_db_ip,
    )
    _bootstrap_ovh_app(
        Connection(host=f"centos@{public_app_ip}", config=ctx.config),
        public_name=public_name,
        private_web_ip=private_web_ip,
        private_app_ip=private_app_ip,
        private_db_ip=private_db_ip,
        environment=environment,
        branch=branch,
    )


def _bootstrap_ovh_web(
    ctx, public_name, private_web_ip, private_app_ip, private_db_ip, contact_email
):
    _setup_private_network_interface(ctx, private_web_ip)
    bootstrap_web(
        ctx,
        public_name=public_name,
        app_host_ip=private_app_ip,
        db_host_ip=private_db_ip,
        ssl="letsencrypt",
        contact_email=contact_email,
    )


def _bootstrap_ovh_db(ctx, private_web_ip, private_app_ip, private_db_ip):
    _setup_private_network_interface(ctx, private_db_ip)
    bootstrap_db(
        ctx,
        app_host_ip=private_app_ip,
        web_host_ip=private_web_ip,
        firewall_zone="internal",
    )


def _bootstrap_ovh_app(
    ctx, public_name, private_web_ip, private_app_ip, private_db_ip, environment, branch
):
    _setup_private_network_interface(ctx, private_app_ip)
    bootstrap_app(ctx, web_host_ip=private_web_ip, firewall_zone="internal")
    deploy_app(
        ctx,
        public_name=public_name,
        listen_address=private_app_ip,
        db_host_ip=private_db_ip,
        environment=environment,
        branch=branch,
        notify_rollbar=False,  # FIXME
    )


def _setup_private_network_interface(ctx, private_ip):
    with template_local_file(
        "files/ifcfg-eth1.template", "files/ifcfg-eth1", {"private_ip": private_ip}
    ):
        changed = sudo_put_if_modified(
            ctx,
            local="files/ifcfg-eth1",
            remote="/etc/sysconfig/network-scripts/ifcfg-eth1",
        )
        if changed:
            ctx.sudo("nmcli connection load /etc/sysconfig/network-scripts/ifcfg-eth1")
            # ctx.sudo("nmcli connection up ifname eth1")
    remove_services(ctx, "mdns", "samba-client", zone="internal")
    set_interface_zone(ctx, interface="eth1", zone="internal")
