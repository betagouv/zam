from fabric.tasks import task

from tools.file import sudo_put
from tools.munin import enable_munin_plugin

# from tools.package import install_packages


@task
def monitoring(ctx):
    """
    Setup basic system monitoring using munin
    """
    # install_packages(
    #     ctx,
    #     "munin",
    #     "munin-node",
    #     # "libdbd-pg-perl",
    #     # "libparse-http-useragent-perl",
    # )
    sudo_put(ctx, "files/munin/munin.conf", "/etc/munin/munin.conf")
    sudo_put(ctx, "files/munin/munin-node.conf", "/etc/munin/munin-node.conf")
    _munin_setup_nginx_plugin(ctx)
    _munin_setup_postgres_plugin(ctx)
    ctx.sudo("systemctl restart munin-node")


def _munin_setup_nginx_plugin(ctx):
    sudo_put(
        ctx, "files/munin/munin-nginx.conf", "/etc/munin/plugin-conf.d/munin-nginx.conf"
    )
    enable_munin_plugin(ctx, "nginx_request")
    enable_munin_plugin(ctx, "nginx_status")


def _munin_setup_postgres_plugin(ctx):
    enable_munin_plugin(ctx, "postgres_autovacuum")
    enable_munin_plugin(ctx, "postgres_bgwriter")
    enable_munin_plugin(ctx, "postgres_cache_", "postgres_cache_zam")
    enable_munin_plugin(ctx, "postgres_checkpoints")
    enable_munin_plugin(ctx, "postgres_connections_", "postgres_connections_zam")
    enable_munin_plugin(ctx, "postgres_connections_db")
    enable_munin_plugin(ctx, "postgres_locks_", "postgres_locks_zam")
    enable_munin_plugin(ctx, "postgres_querylength_", "postgres_querylength_zam")
    enable_munin_plugin(ctx, "postgres_scans_", "postgres_scans_zam")
    enable_munin_plugin(ctx, "postgres_size_", "postgres_size_zam")
    enable_munin_plugin(ctx, "postgres_transactions_", "postgres_transactions_zam")
    enable_munin_plugin(ctx, "postgres_tuples_", "postgres_tuples_zam")
    enable_munin_plugin(ctx, "postgres_users")
    enable_munin_plugin(ctx, "postgres_xlog")
