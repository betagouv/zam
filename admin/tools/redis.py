from .command import command
from .package import install_packages, is_package_installed
from .system import SystemSpecificCommand


class AddRedisRepository(SystemSpecificCommand):
    def debian(self, ctx):
        pass

    def redhat(self, ctx):
        """Add CentOS EPEL repository"""
        changed = False
        if not is_package_installed(ctx, "epel-release"):
            changed = True
        return changed


add_redis_repository = AddRedisRepository()


@command
def install_redis(ctx):
    """Install Redis"""
    if not is_package_installed(ctx, "redis"):
        install_packages(ctx, "redis")


class RedisServiceName(SystemSpecificCommand):
    def debian(self, ctx):
        return "redis-server"

    def redhat(self, ctx):
        return "redis"


redis_service_name = RedisServiceName()
