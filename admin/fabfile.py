from tasks.backup import *
from tasks.deploy import *
from tasks.monitoring import *
from tasks.system import *


@task
def bootstrap(ctx, hostname="", os_storage_url="", os_auth_token=""):
    if hostname:
        set_hostname(ctx, hostname)
    system(ctx)
    monitoring(ctx)
    http(ctx)
    letsencrypt(ctx)
    basicauth(ctx)
    # Now put the https ready Nginx conf.
    http(ctx)
    setup_backups(ctx, os_storage_url, os_auth_token)


@task
def logs_webapp(ctx, lines=100):
    ctx.sudo(f"journalctl --unit zam_webapp.service -n {lines}")


@task
def logs_worker(ctx, lines=100):
    ctx.sudo(f"journalctl --unit zam_worker.service -n {lines}")


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
