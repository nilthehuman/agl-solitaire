from setuptools import setup

from src.agl_solitaire.version import get_version

setup(
    name="agl_solitaire",
    version=get_version(),
    entry_points={
        "console_scripts": [
            "agl-solitaire = agl_solitaire.__main__:main",
        ],
    },
)
