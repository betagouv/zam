import posixpath

from fabric import task

from tasks.system import setup_common
from tools import timestamp
from tools.command import command
from tools.file import append, create_directory, is_directory, sudo_put_if_modified
from tools.firewalld import add_service, enable_firewall, start_firewall
from tools.postgres import (
    add_postgres_repository,
    create_postgres_database,
    create_postgres_user,
    initialize_postgres,
    install_postgres,
    postgres_config_dir,
    postgres_database_exists,
    postgres_service_name,
    postgres_user_exists,
    run_as_postgres,
)
from tools.systemd import (
    enable_service,
    is_service_started,
    restart_service,
    start_service,
    stop_service,
)


@task
def bootstrap_db(
    ctx,
    hostname="",
    dbname="zam",
    dbuser="zam",
    dbpassword="iloveamendements",
    web_host_ip=None,
    app_host_ip=None,
    firewall_zone="public",
):
    print("\033[95m=== Bootstrapping db server ===\033[0m")
    setup_common(ctx, hostname=hostname, munin_server_ip=web_host_ip)

    enable_firewall(ctx)
    start_firewall(ctx)
    add_service(ctx, "munin-node", zone=firewall_zone)  # port 4949
    add_service(ctx, "postgresql", zone=firewall_zone)  # port 5432

    setup_postgres(ctx, app_host_ip=app_host_ip)
    setup_zam_database(ctx, dbname, dbuser, dbpassword)


def setup_postgres(ctx, app_host_ip):
    add_postgres_repository(ctx)
    install_postgres(ctx)
    initialize_postgres(ctx)

    config_dir = postgres_config_dir(ctx)

    config_changed = False
    config_changed |= customize_postgres_config(ctx, config_dir)

    if app_host_ip:
        config_changed |= configure_host_based_access(ctx, config_dir, app_host_ip)

    postgres_service = postgres_service_name(ctx)

    if config_changed:
        restart_service(ctx, postgres_service)
    elif not is_service_started(ctx, postgres_service):
        start_service(ctx, postgres_service)

    enable_service(ctx, postgres_service)


@command
def customize_postgres_config(ctx, config_dir):
    """Customize Postgres configuration"""
    extra_config_dir = posixpath.join(config_dir, "conf.d")
    if not is_directory(ctx, extra_config_dir):
        create_directory(ctx, extra_config_dir, owner="postgres")
    config_changed = False
    config_changed |= append(
        ctx,
        filename=posixpath.join(config_dir, "postgresql.conf"),
        line="include_dir = 'conf.d'",
        user="postgres",
    )
    config_changed |= sudo_put_if_modified(
        ctx,
        local="files/postgres.conf",
        remote=posixpath.join(config_dir, "conf.d/zam.conf"),
        chown="postgres",
    )
    return config_changed


@command
def configure_host_based_access(ctx, config_dir, app_host_ip):
    """Customize Postgres host-based authentication"""
    config_changed = append(
        ctx,
        filename=posixpath.join(config_dir, "pg_hba.conf"),
        line=f"host\tall\t\tall\t\t{app_host_ip}/32\t\tmd5",
        user="postgres",
    )
    return config_changed


def setup_zam_database(
    ctx, dbname, dbuser, dbpassword, encoding="UTF8", locale="en_US.UTF8"
):
    if not postgres_user_exists(ctx, dbuser):
        create_postgres_user(ctx, dbuser, dbpassword)

    if not postgres_database_exists(ctx, dbname):
        create_postgres_database(ctx, dbname, dbuser, encoding, locale)


@task
def wipe_db(ctx, dbname):
    backup_db(ctx, dbname)
    # Will be restarted later in `deploy_repondeur`.
    stop_service(ctx, "zam_webapp")
    stop_service(ctx, "zam_worker")
    run_as_postgres(ctx, f"dropdb {dbname}")


@task
def backup_db(ctx, dbname="zam"):
    create_directory(ctx, "/var/backups/zam", owner="postgres")
    backup_filename = f"/var/backups/zam/postgres-dump-{timestamp()}.sql"
    run_as_postgres(
        ctx,
        f"pg_dump --dbname={dbname} --create --encoding=UTF8 --file={backup_filename}",
    )
