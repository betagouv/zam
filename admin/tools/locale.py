from .system import SystemSpecificCommand


class InstallLocale(SystemSpecificCommand):
    def redhat(self, ctx, locale_name):
        """
        Install {} locale
        """
        installed_locales = [
            line.strip()
            for line in ctx.sudo(f"locale -a", hide=True).stdout.splitlines()
        ]
        if locale_name not in installed_locales:
            ctx.sudo(f"yum --quiet --assumeyes reinstall glibc-common")


install_locale = InstallLocale()
