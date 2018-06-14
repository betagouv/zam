from setuptools import setup, find_packages


setup(
    name="zam-aspirateur",
    version="0.1.0",
    url="https://github.com/betagouv/zam",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    entry_points={"console_scripts": ["zam-aspirateur = zam_aspirateur.__main__:main"]},
    install_requires=[
        "bleach",
        "cachecontrol",
        "dataclasses",
        "lockfile",
        "openpyxl",
        "requests",
        "selectolax",
        "xmltodict",
    ],
)
