import hashlib
from pathlib import Path
from shlex import quote


def is_file(ctx, path, user=None):
    return ctx.sudo(f"[ -f {quote(path)} ]", warn=True, hide=True, user=user).ok


def is_link(ctx, path, user=None):
    return ctx.sudo(f"[ -L {quote(path)} ]", warn=True, hide=True, user=user).ok


def is_directory(ctx, path, user=None):
    return ctx.sudo(f"[ -d {quote(path)} ]", warn=True, hide=True, user=user).ok


def create_directory(ctx, path, owner):
    ctx.sudo(f"mkdir -p {quote(path)}")
    ctx.sudo(f"chown {owner}: {quote(path)}")


def sudo_put(ctx, local, remote, chown="root"):
    tmp = str(Path("/tmp") / hashlib.md5(remote.encode()).hexdigest())
    ctx.put(local, tmp)
    ctx.sudo(f"mv {quote(tmp)} {quote(remote)}")
    if chown:
        ctx.sudo(f"chown {chown}: {quote(remote)}")


def sudo_put_if_modified(ctx, local, remote, chown="root"):
    if not is_file(ctx, remote) or md5(ctx, remote, use_sudo=True) != local_md5(local):
        sudo_put(ctx, local, remote, chown=chown)
        return True
    return False


def put_dir(ctx, local, remote, chown=None):
    local = Path(local)
    remote = Path(remote)
    for path in local.rglob("*"):
        relative_path = path.relative_to(local)
        if str(relative_path).startswith("."):
            # Avoid pushing hidden files.
            continue
        if path.is_dir():
            ctx.sudo(f"mkdir -p {quote(remote / relative_path)}")
        else:
            sudo_put(ctx, str(path), str(remote / relative_path), chown)


def sed(ctx, filename, match, replace):
    ctx.sudo(f"sed -i 's/{match}/{replace}/' {quote(filename)}")


def append(ctx, filename, line, user=None):
    if (
        line
        and is_file(ctx, filename, user=user)
        and contains_line(ctx, filename, line, user=user)
    ):
        return False
    sudo_prefix = "sudo"
    if user is not None:
        sudo_prefix += f" -u {user}"
    ctx.run(f"echo {quote(line)} | {sudo_prefix} tee -a {quote(filename)} >/dev/null")
    return True


def contains_line(ctx, filename, line, user=None):
    command = f"grep --fixed-strings --line-regexp {quote(line)} {quote(filename)}"
    return ctx.sudo(command, warn=True, hide=True, user=user).ok


def md5(ctx, filename, use_sudo=False):
    run = ctx.sudo if use_sudo else ctx.run
    res = run(f"md5sum {quote(filename)}", hide=True)
    return res.stdout.strip().split()[0]


def local_md5(filename):
    with open(filename, "rb") as f_:
        return hashlib.md5(f_.read()).hexdigest()
