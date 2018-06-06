from setuptools import find_packages, setup


setup(
    name="zam-visionneuse",
    version="0.1.0",
    url="https://github.com/betagouv/zam",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    entry_points={
        "console_scripts": ["zam-visionneuse = zam_visionneuse.__main__:main"]
    },
    install_requires=["CommonMark", "dataclasses", "Jinja2", "Logbook", "wrapt"],
)
