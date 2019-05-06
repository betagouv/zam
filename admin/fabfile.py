from tasks.backup import *
from tasks.deploy import *
from tasks.monitoring import *
from tasks.system import *


@task
def bootstrap(ctx, hostname="", os_storage_url="", os_auth_token=""):
    if hostname:
        set_hostname(ctx, hostname)
    else:
        hostname = ctx.run("hostname").stdout.strip()

    system(ctx)
    monitoring(ctx)
    setup_backups(ctx, os_storage_url, os_auth_token)
    http(ctx, ssl=False)

    # Add password if not set
    if not ctx.sudo("grep -q demozam /etc/nginx/.htpasswd", warn=True).ok:
        basicauth(ctx)

    # We need DNS to be configured before we can set up SSL
    if ctx.host == hostname:
        letsencrypt(ctx)
    else:
        print("Using a self-signed certificate because DNS is not configured yet")
        setup_self_signed_cert(ctx)

    # Now put the https ready Nginx conf.
    http(ctx, ssl=True)


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
