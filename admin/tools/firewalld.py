from shlex import quote

from .package import install_packages, is_package_installed
from .systemd import enable_service, is_service_started, start_service


def install_firewall(ctx):
    if not is_package_installed(ctx, "firewalld"):
        install_packages(ctx, "firewalld")


def enable_firewall(ctx):
    enable_service(ctx, "firewalld")


def start_firewall(ctx):
    if not is_service_started(ctx, "firewalld"):
        start_service(ctx, "firewalld")


def set_interface_zone(ctx, interface, zone):
    ctx.sudo(f"firewall-cmd --change-interface={quote(interface)} --zone={quote(zone)}")


def add_ports(ctx, *ports, protocol="tcp", zone="public"):
    for port in ports:
        ctx.sudo(f"firewall-cmd --permanent --zone={zone} --add-port={port}/{protocol}")
    ctx.sudo(f"firewall-cmd --reload")


add_port = add_ports


def remove_ports(ctx, *ports, protocol="tcp", zone="public"):
    for port in ports:
        ctx.sudo(
            f"firewall-cmd --permanent --zone={zone} --remove-port={port}/{protocol}"
        )
    ctx.sudo(f"firewall-cmd --reload")


remove_port = remove_ports


def add_services(ctx, *services, zone="public"):
    for service in services:
        ctx.sudo(f"firewall-cmd --permanent --zone={zone} --add-service={service}")
    ctx.sudo(f"firewall-cmd --reload")


add_service = add_services


def remove_services(ctx, *services, zone="public"):
    for service in services:
        ctx.sudo(f"firewall-cmd --permanent --zone={zone} --remove-service={service}")
    ctx.sudo(f"firewall-cmd --reload")


remove_service = remove_services
