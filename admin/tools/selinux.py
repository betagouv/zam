from shlex import quote

from .file import is_file


def is_selinux_enabled(ctx):
    return (
        is_file(ctx, "/usr/sbin/selinuxenabled")
        and ctx.run("/usr/sbin/selinuxenabled", warn=True, hide=True).ok
    )


def set_selinux_bool(ctx, name, value, persistent=True):
    flags = "-P" if persistent else ""
    ctx.sudo(f"setsebool {flags} {quote(name)} {quote(value)}")
