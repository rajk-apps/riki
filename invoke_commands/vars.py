import toml
import importlib

pytom = toml.load("pyproject.toml")
package_name = pytom["project"]["name"]
author_name = " - ".join(pytom["project"]["authors"])

doc_dir_name = "docs"
doctest_notebooks_glob = "notebooks/doc-*.ipynb"

mymodule = importlib.import_module(package_name)

boilerplate_branch = "master"
