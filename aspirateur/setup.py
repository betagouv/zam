from setuptools import setup


setup(
    name='zam-aspirateur',
    version='0.1.0',
    url='https://github.com/betagouv/zam',
    entry_points={
        'console_scripts': [
            'zam-aspirateur = zam_aspirateur.__main__:main',
        ],
    },
    install_requires=[
        'bleach',
        'dataclasses',
        'openpyxl',
        'requests',
    ],
)
