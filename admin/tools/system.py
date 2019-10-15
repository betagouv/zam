from .command import Command
from .file import is_file


def cpu_count(ctx):
    return int(ctx.run("cat /proc/cpuinfo | grep Processor | wc -l").stdout.strip())


def distribution_name(ctx):
    """
    Get the OS distribution name.
    """

    kernel = ctx.run("uname -s", hide=True).stdout.strip()

    if kernel == "Linux":
        if is_file(ctx, "/usr/bin/lsb_release"):
            id_ = ctx.run("lsb_release --id --short", hide=True).stdout.strip()
            return id_
        else:
            if is_file(ctx, "/etc/debian_version"):
                return "Debian"
            elif is_file(ctx, "/etc/fedora-release"):
                return "Fedora"
            elif is_file(ctx, "/etc/redhat-release"):
                release = ctx.run("cat /etc/redhat-release", hide=True).stdout.strip()
                if release.startswith("Red Hat Enterprise Linux"):
                    return "RHEL"
                elif release.startswith("CentOS"):
                    return "CentOS"
                elif release.startswith("Scientific Linux"):
                    return "SLES"
    return "unknown"


def distribution_family(ctx):
    """
    Get the OS distribution family.
    """
    return _distribution_family_from_id(distribution_name(ctx))


def _distribution_family_from_id(distribution_name):
    if distribution_name in ["Debian", "Ubuntu", "LinuxMint", "elementary OS"]:
        return "debian"
    elif distribution_name in ["RHEL", "CentOS", "SLES", "Fedora"]:
        return "redhat"
    else:
        return "unknown"


class SystemSpecificCommand(Command):
    """
    Dispatch call to distribution or family specific implementation
    """

    def dispatch(self, ctx):
        distribution = distribution_name(ctx)
        family = _distribution_family_from_id(distribution)
        method = getattr(self, distribution, getattr(self, family, None))
        if method is None:
            raise NotImplementedError(
                f"{distribution!r} not supported for {self.__class__.__name__}"
            )
        return method
