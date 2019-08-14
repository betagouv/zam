from hashlib import sha256
from typing import BinaryIO, Dict, cast

from pyramid.config import Configurator
from pyramid.path import AssetResolver
from pyramid.path import PkgResourcesAssetDescriptor as AssetDescriptor
from pyramid.request import Request
from pyramid.static import QueryStringCacheBuster


def includeme(config: Configurator) -> None:
    config.add_static_view("static", "static", cache_max_age=3600)
    config.add_cache_buster(
        "zam_repondeur:static/",
        ContentHashCacheBuster(package="zam_repondeur", base_path="static/"),
    )


class ContentHashCacheBuster(QueryStringCacheBuster):
    def __init__(self, package: str, base_path: str, param: str = "x") -> None:
        super().__init__(param=param)
        self.asset_resolver = AssetResolver(package)
        self.base_path = base_path
        self.token_cache: Dict[str, str] = {}

    def tokenize(self, request: Request, subpath: str, kw: Dict[str, str]) -> str:
        token = self.token_cache.get(subpath)
        if token is None:
            asset = self._resolve_asset(subpath)
            self.token_cache[subpath] = token = self._hash_asset(asset)
        return token

    def _resolve_asset(self, subpath: str) -> AssetDescriptor:
        return self.asset_resolver.resolve(self.base_path + subpath)

    def _hash_asset(self, asset: AssetDescriptor) -> str:
        hash_ = sha256()
        with cast(BinaryIO, asset.stream()) as stream:
            for block in iter(lambda: stream.read(4096), b""):
                hash_.update(block)
        return hash_.hexdigest()
