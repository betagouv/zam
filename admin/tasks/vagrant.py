from io import StringIO

from fabric import task
from fabric.config import Config
from fabric.connection import Connection
from invoke import run
from paramiko.config import SSHConfig

from .app import bootstrap_app
from .db import bootstrap_db
from .deploy import deploy_app
from .web import bootstrap_web

VAGRANT_WEB_IP = "192.168.10.33"
VAGRANT_APP_IP = "192.168.10.34"
VAGRANT_DB_IP = "192.168.10.35"


@task
def vagrant(ctx, branch="master"):
    """
    Configure a Vagrant multi-machine virtual infrastructure
    """
    vagrant_web(ctx)
    vagrant_db(ctx)
    vagrant_app(ctx, branch=branch)


@task
def vagrant_web(ctx):
    """
    Configure the web tier
    """
    web_conn = vagrant_connection("web")
    bootstrap_web(
        web_conn,
        public_name="zam.127.0.0.1.nip.io",
        app_host_ip=VAGRANT_APP_IP,
        db_host_ip=VAGRANT_DB_IP,
        ssl="self-signed",
        ssl_redir_port="9443",
    )


@task
def vagrant_app(ctx, branch="master"):
    """
    Configure the application tier
    """
    app_conn = vagrant_connection("app")
    bootstrap_app(app_conn, web_host_ip=VAGRANT_WEB_IP)
    deploy_app(
        app_conn,
        public_name="zam.127.0.0.1.nip.io",
        listen_address=VAGRANT_APP_IP,
        db_host_ip=VAGRANT_DB_IP,
        environment="vagrant",
        branch=branch,
        notify_rollbar=False,
    )


@task
def vagrant_db(ctx):
    """
    Configure the database tier
    """
    db_conn = vagrant_connection("db")
    bootstrap_db(db_conn, app_host_ip="192.168.10.34", web_host_ip=VAGRANT_WEB_IP)


def vagrant_connection(name):
    output = run(f"vagrant ssh-config {name}", hide=True).stdout
    ssh_config = SSHConfig()
    ssh_config.parse(StringIO(output))
    config = Config(ssh_config=ssh_config, project_location=".")
    config.load_project()
    config.run.echo = True
    return Connection(host=name, config=config)
