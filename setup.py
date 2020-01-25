import toml
import os
import importlib
from setuptools import find_packages, setup

pytom = toml.load("pyproject.toml")
package_name = pytom["project"]["name"]
author_name = " - ".join(pytom["project"]["authors"])

mymodule = importlib.import_module(package_name)

data_subdirs = ["templates", "static"]

data_files = []

for subdir in data_subdirs:
    for dir_path, _, file_names in os.walk(os.path.join(package_name, subdir)):
        data_files += [os.path.join(dir_path, f) for f in file_names]


with open("README.md") as fp:
    long_description = fp.read()

with open("requirements.txt") as fp:
    requirements = fp.read().strip().split()

if __name__ == "__main__":
    setup(
        name=package_name,
        version=mymodule.__version__,
        description=pytom["project"]["description"],
        long_description=long_description,
        license="MIT",
        classifiers=["License :: OSI Approved :: MIT License"],
        url=pytom["project"]["url"],
        keywords=pytom["project"].get("keywords"),
        author=author_name,
        packages=[p for p in find_packages() if p != "invoke_commands"],
        data_files=[("out", data_files),],
        include_package_data=True,
        python_requires=pytom["project"]["python"],
        platforms="any",
        install_requires=requirements,
    )
