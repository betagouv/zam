import posixpath
from shlex import quote

from .file import is_directory
from .run import sudo_in_dir


def clone_or_update_repo(ctx, repo, branch, parent_dir, name, user):
    path = posixpath.join(parent_dir, name)
    if not is_directory(ctx, path, user=user):
        clone_repo(ctx, repo, branch, parent_dir, name, user)
    else:
        update_repo(ctx, branch, path, user)


def clone_repo(ctx, repo, branch, parent_dir, name, user):
    sudo_in_dir(
        ctx,
        command=f"git clone --branch={branch} {repo} {quote(name)}",
        directory=parent_dir,
        user=user,
    )


def update_repo(ctx, branch, path, user):
    sudo_in_dir(ctx, f"git fetch", directory=path, user=user)
    sudo_in_dir(ctx, f"git checkout {branch}", directory=path, user=user)
    sudo_in_dir(ctx, f"git reset --hard origin/{branch}", directory=path, user=user)
