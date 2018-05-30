from setuptools import setup


setup(
    name="zam-visionneuse",
    version="0.1.0",
    url="https://github.com/betagouv/zam",
    entry_points={
        "console_scripts": [
            "zam-visionneuse = zam_visionneuse.__main__:generate"
        ]
    },
)
