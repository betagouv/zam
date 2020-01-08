from shlex import quote


def create_user(ctx, name, system=True, home_dir=None, shell=None):
    args = []
    if system:
        args.append("--system")
    if home_dir is not None:
        args.append(f"--create-home --home-dir {quote(home_dir)}")
    if shell is not None:
        args.append(f"--shell {quote(shell)}")
    args.append(name)
    command = "useradd " + " ".join(args)
    ctx.sudo(command)


def user_exists(ctx, name):
    return ctx.sudo(f"getent passwd {name}", warn=True, hide=True).ok
