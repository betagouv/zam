from fabric.tasks import task

from tools import template_local_file
from tools.file import sudo_put


@task
def setup_backups(
    ctx,
    os_storage_url="",
    os_tenant_id="",
    os_tenant_name="",
    os_username="",
    os_password="",
):
    ctx.sudo("python3 -m pip install rotate-backups")
    with template_local_file(
        "files/cron-zam-backups.sh.template",
        "files/cron-zam-backups.sh",
        {
            "os_storage_url": os_storage_url,
            "os_tenant_id": os_tenant_id,
            "os_tenant_name": os_tenant_name,
            "os_username": os_username,
            "os_password": os_password,
        },
    ):
        sudo_put(ctx, "files/cron-zam-backups.sh", "/etc/cron.hourly/zam-backups")

    ctx.sudo("chmod 755 /etc/cron.hourly/zam-backups")
