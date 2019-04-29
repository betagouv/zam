from fabric.tasks import task

from tools import sudo_put, template_local_file


@task
def setup_backups(ctx, os_storage_url="", os_auth_token=""):
    ctx.sudo("python3 -m pip install rotate-backups")
    with template_local_file(
        "cron-zam-backups.sh.template",
        "cron-zam-backups.sh",
        {"os_storage_url": os_storage_url, "os_auth_token": os_auth_token},
    ):
        sudo_put(ctx, "cron-zam-backups.sh", "/etc/cron.hourly/zam-backups")

    ctx.sudo("chmod 755 /etc/cron.hourly/zam-backups")
