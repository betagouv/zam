from shlex import quote


def sudo_in_dir(ctx, command, directory, user, shell="/bin/bash -c", **kwargs):
    prefixed_command = f"cd {quote(directory)} && {command}"
    shell_wrapped_command = f"{shell} {quote(prefixed_command)}"
    return ctx.sudo(shell_wrapped_command, user=user, **kwargs)
