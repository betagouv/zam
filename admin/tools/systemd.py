from shlex import quote

from .command import command


@command
def enable_service(ctx, name):
    """Enable {} service to start on boot"""
    ctx.sudo(f"systemctl enable {quote(name)}")


@command
def start_service(ctx, name):
    """Start {} service"""
    ctx.sudo(f"systemctl start {quote(name)}")


@command
def stop_service(ctx, name):
    """Stop {} service"""
    ctx.sudo(f"systemctl stop {quote(name)}")


@command
def restart_service(ctx, name):
    """Restart {} service"""
    ctx.sudo(f"systemctl restart {quote(name)}")


@command
def reload_service(ctx, name):
    """Reload {} service"""
    ctx.sudo(f"systemctl reload {quote(name)}")


def is_service_started(ctx, name):
    return ctx.sudo(f"systemctl status {quote(name)}", warn=True, hide=True).ok
