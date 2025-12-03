from setuptools import setup, find_packages

setup(
    name="ajanta",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "ajanta=ajanta.cli.main:main",
        ],
    },
)
