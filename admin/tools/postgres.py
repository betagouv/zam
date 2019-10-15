from shlex import quote

from .command import command
from .file import is_file
from .package import install_packages, is_package_installed
from .system import SystemSpecificCommand


class AddPostgresRepository(SystemSpecificCommand):
    def debian(self, ctx):
        raise NotImplementedError  # TODO: should we use distro package or PGDG?

    def redhat(self, ctx):
        """Add official PGDG repo"""
        changed = False
        if not is_package_installed(ctx, "pgdg-redhat-repo"):
            install_packages(
                ctx,
                "https://download.postgresql.org/pub/repos/yum/11/redhat/rhel-7-x86_64/"
                "pgdg-centos11-11-2.noarch.rpm",
            )
            changed = True
        return changed


add_postgres_repository = AddPostgresRepository()


class InstallPostgres(SystemSpecificCommand):
    """Install Postgres server"""

    def debian(self, ctx):
        raise NotImplementedError  # TODO

    def redhat(self, ctx):
        changed = False
        if not is_package_installed(ctx, "postgresql11-server"):
            install_packages(ctx, "postgresql11-server")
            changed = True
        return changed


install_postgres = InstallPostgres()


class InitializePostgres(SystemSpecificCommand):
    def debian(self, ctx):
        pass  # already initialized by package install

    def redhat(self, ctx):
        """Initialize database directory"""
        if not is_file(ctx, "/var/lib/pgsql/11/data/PG_VERSION"):
            ctx.sudo("/usr/pgsql-11/bin/postgresql-11-setup initdb")


initialize_postgres = InitializePostgres()


def postgres_user_exists(ctx, name):
    res = run_as_postgres(
        ctx,
        f'''psql -t -A -c "SELECT COUNT(*) FROM pg_user WHERE usename = '{name}';"''',
        hide=True,
    )
    return res.stdout.strip() == "1"


@command
def create_postgres_user(ctx, dbuser, dbpassword):
    """Create Postgres user {}"""
    sql = f"CREATE USER {dbuser} ENCRYPTED PASSWORD '{dbpassword}';"
    run_as_postgres(ctx, f'psql -c "{sql}" || exit 0', hide=True)


def postgres_database_exists(ctx, dbname):
    res = run_as_postgres(
        ctx, f'''psql -d {quote(dbname)} -c "SELECT 1;"''', warn=True, hide=True
    )
    return res.ok


@command
def create_postgres_database(ctx, dbname, owner, encoding, locale):
    """Create Postgres database {}"""
    run_as_postgres(
        ctx,
        (
            f"createdb --owner={owner} --template=template0 --encoding={encoding} "
            f"--lc-ctype={locale} --lc-collate={locale} {dbname} || exit 0"
        ),
    )


def run_as_postgres(ctx, cmd, **kwargs):
    return ctx.run(f"sudo -Hiu postgres {cmd}", **kwargs)


class PostgresConfigDir(SystemSpecificCommand):
    def debian(self, ctx):
        raise NotImplementedError  # TODO

    def redhat(self, ctx):
        return "/var/lib/pgsql/11/data/"


postgres_config_dir = PostgresConfigDir()


class PostgresServiceName(SystemSpecificCommand):
    def debian(self, ctx):
        raise NotImplementedError  # TODO

    def redhat(self, ctx):
        return "postgresql-11"


postgres_service_name = PostgresServiceName()
