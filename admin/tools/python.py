from .command import command
from .package import install_packages, is_package_installed
from .system import SystemSpecificCommand


class AddPythonRepository(SystemSpecificCommand):
    def debian(self, ctx):
        pass

    def redhat(self, ctx):
        """Add Software Collections (SCL) repository"""
        changed = False
        if not is_package_installed(ctx, "centos-release-scl"):
            install_packages(ctx, "centos-release-scl")
            changed = True
        return changed


add_python_repository = AddPythonRepository()


@command
def install_python(ctx):
    """Install Python 3.x"""
    if not is_package_installed(ctx, "python3"):
        install_packages(ctx, "python3")
