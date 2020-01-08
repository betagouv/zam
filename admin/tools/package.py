from shlex import quote

from .system import SystemSpecificCommand


class UpdatePackageCache(SystemSpecificCommand):
    def debian(self, ctx):
        ctx.sudo("apt-get update", hide=True)

    def redhat(self, ctx):
        ctx.sudo("yum makecache", hide=True)


update_package_cache = UpdatePackageCache()


class IsPackageInstalled(SystemSpecificCommand):
    def debian(self, ctx, name):
        res = ctx.run(f"dpkg -s {quote(name)}", hide=True, warn=True)
        for line in res.splitlines():
            if line.startswith("Status: "):
                status = line[8:]
                if "installed" in status.split(" "):
                    return True
        return False

    def redhat(self, ctx, name):
        return ctx.run(f"rpm --query {name}", warn=True, hide=True).ok


is_package_installed = IsPackageInstalled()


class InstallPackages(SystemSpecificCommand):
    def redhat(self, ctx, *names):
        args = [
            "--quiet",
            "--assumeyes",
            "--setopt=skip_missing_names_on_install=False",
        ]
        args.extend(quote(name) for name in names)
        ctx.sudo("yum install " + " ".join(args))


install_package = install_packages = InstallPackages()


class InstallPackageUpdates(SystemSpecificCommand):
    def redhat(self, ctx, *names):
        args = ["--assumeyes"]
        ctx.sudo("yum update " + " ".join(args))


install_package_updates = InstallPackageUpdates()
