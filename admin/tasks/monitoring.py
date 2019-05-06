from fabric.tasks import task

from tools import install_packages, sudo_put


@task
def monitoring(ctx):
    """
    Setup basic system monitoring using munin
    """
    install_packages(
        ctx, "munin", "munin-node", "libdbd-pg-perl", "libparse-http-useragent-perl"
    )
    sudo_put(ctx, "files/munin/munin.conf", "/etc/munin/munin.conf")
    sudo_put(ctx, "files/munin/munin-node.conf", "/etc/munin/munin-node.conf")
    _munin_setup_nginx_plugin(ctx)
    _munin_setup_postgres_plugin(ctx)
    _munin_setup_redis_plugin(ctx)
    ctx.sudo("systemctl restart munin-node")


def _munin_setup_nginx_plugin(ctx):
    sudo_put(
        ctx, "files/munin/munin-nginx.conf", "/etc/munin/plugin-conf.d/munin-nginx.conf"
    )
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/nginx_request' '/etc/munin/plugins/nginx_request'"
    )
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/nginx_status' '/etc/munin/plugins/nginx_status'"
    )


def _munin_setup_postgres_plugin(ctx):
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/postgres_autovacuum' '/etc/munin/plugins/postgres_autovacuum'"
    )
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/postgres_bgwriter' '/etc/munin/plugins/postgres_bgwriter'"
    )
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/postgres_cache_' '/etc/munin/plugins/postgres_cache_zam'"
    )
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/postgres_checkpoints' '/etc/munin/plugins/postgres_checkpoints'"
    )
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/postgres_connections_' '/etc/munin/plugins/postgres_connections_zam'"
    )
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/postgres_connections_db' '/etc/munin/plugins/postgres_connections_db'"
    )
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/postgres_locks_' '/etc/munin/plugins/postgres_locks_zam'"
    )
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/postgres_querylength_' '/etc/munin/plugins/postgres_querylength_zam'"
    )
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/postgres_scans_' '/etc/munin/plugins/postgres_scans_zam'"
    )
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/postgres_size_' '/etc/munin/plugins/postgres_size_zam'"
    )
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/postgres_transactions_' '/etc/munin/plugins/postgres_transactions_zam'"
    )
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/postgres_tuples_' '/etc/munin/plugins/postgres_tuples_zam'"
    )
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/postgres_users' '/etc/munin/plugins/postgres_users'"
    )
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/postgres_xlog' '/etc/munin/plugins/postgres_xlog'"
    )
    ctx.sudo("rm -f /etc/munin/plugins/postgres_cache_ALL")
    ctx.sudo("rm -f /etc/munin/plugins/postgres_connections_ALL")
    ctx.sudo("rm -f /etc/munin/plugins/postgres_locks_ALL")
    ctx.sudo("rm -f /etc/munin/plugins/postgres_querylength_ALL")
    ctx.sudo("rm -f /etc/munin/plugins/postgres_size_ALL")
    ctx.sudo("rm -f /etc/munin/plugins/postgres_transactions_ALL")


def _munin_setup_redis_plugin(ctx):
    sudo_put(ctx, "files/munin/munin-redis.sh", "/usr/share/munin/plugins/redis_")
    ctx.sudo("chmod +x /usr/share/munin/plugins/redis_")
    ctx.sudo(
        "ln -sf '/usr/share/munin/plugins/redis_' '/etc/munin/plugins/redis_127.0.0.1_6379'"
    )
