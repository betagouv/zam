from .package import install_packages
from .system import SystemSpecificCommand


class InstallCertbot(SystemSpecificCommand):
    """Install Certbot"""

    def debian(self, ctx):
        raise NotImplementedError  # TODO

    def redhat(self, ctx):
        install_packages(ctx, "epel-release")
        install_packages(ctx, "certbot", "python2-certbot-nginx")


install_certbot = InstallCertbot()
