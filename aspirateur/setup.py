from setuptools import setup, find_packages


setup(
    name="zam-aspirateur",
    version="0.1.0",
    url="https://github.com/betagouv/zam",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        "bleach",
        "cachecontrol",
        "dataclasses",
        "inscriptis",
        "lockfile",
        "openpyxl",
        "requests",
        "selectolax",
    ],
)
