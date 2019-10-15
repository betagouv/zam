from .command import command
from .package import install_packages, is_package_installed
from .system import SystemSpecificCommand


class AddNginxRepository(SystemSpecificCommand):
    def debian(self, ctx):
        pass

    def redhat(self, ctx):
        """Add CentOS EPEL repository"""
        changed = False
        if not is_package_installed(ctx, "epel-release"):
            install_packages(ctx, "epel-release")
            changed = True
        return changed


add_nginx_repository = AddNginxRepository()


@command
def install_nginx(ctx):
    """Install Nginx"""
    changed = False
    if not is_package_installed(ctx, "nginx"):
        install_packages(ctx, "nginx")
        changed = True
    return changed
