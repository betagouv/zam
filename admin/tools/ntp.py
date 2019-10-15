from .package import install_packages, is_package_installed
from .system import SystemSpecificCommand


class InstallNTP(SystemSpecificCommand):
    """Install NTP server"""

    def debian(self, ctx):
        raise NotImplementedError  # TODO

    def redhat(self, ctx):
        if not is_package_installed(ctx, "ntp"):
            install_packages(ctx, "ntp")


install_ntp = InstallNTP()


class NTPServiceName(SystemSpecificCommand):
    def debian(self, ctx):
        raise NotImplementedError  # TODO

    def redhat(self, ctx):
        return "ntpd"


ntp_service_name = NTPServiceName()
