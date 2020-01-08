import posixpath
from shlex import quote

from .command import command
from .file import is_file, is_link
from .package import install_packages, is_package_installed
from .system import SystemSpecificCommand


class AddMuninRepository(SystemSpecificCommand):
    def debian(self, ctx):
        pass

    def redhat(self, ctx):
        """Add CentOS EPEL repository"""
        changed = False
        if not is_package_installed(ctx, "epel-release"):
            install_packages(ctx, "epel-release")
            changed = True
        return changed


add_munin_repository = AddMuninRepository()


@command
def install_munin(ctx):
    if not is_package_installed(ctx, "munin"):
        install_packages(ctx, "munin")


@command
def add_monitored_node(ctx, name, address):
    path = posixpath.join("/etc/munin/conf.d", f"{name}.conf")
    if not is_file(ctx, path):
        contents = f"[{name}]\n    address {address}\n    use_node_name yes\n"
        ctx.run(f"echo -e '{contents}' | sudo tee >/dev/null {quote(path)}")


@command
def install_munin_node(ctx):
    if not is_package_installed(ctx, "munin-node"):
        install_packages(ctx, "munin-node")


def munin_node_service_name(ctx):
    return "munin-node"


class MuninGraphsPath(SystemSpecificCommand):
    def debian(self, ctx):
        raise "/var/cache/munin/www"

    def redhat(self, ctx):
        return "/var/www/html/munin"


munin_graphs_path = MuninGraphsPath()


@command
def enable_munin_plugin(ctx, plugin_name, link_name=None):
    plugin_path = posixpath.join("/usr/share/munin/plugins", plugin_name)
    if link_name is None:
        link_name = plugin_name
    link_path = posixpath.join("/etc/munin/plugins", link_name)
    if not is_link(ctx, link_path):
        ctx.sudo(f"ln -s {plugin_path} {link_path}")
