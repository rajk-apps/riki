import toml
from invoke import task
import glob
import os

pytom = toml.load("pyproject.toml")
package_name = pytom["project"]["name"]
author_name = " - ".join(pytom["project"]["authors"])

doc_dir_name = "docs"
doc_notebooks_dir = "notebooks"


@task
def build(c):

    c.run(
        'sphinx-quickstart {} -p {} -a "{}" -q --ext-autodoc'.format(
            doc_dir_name, package_name, author_name
        )
    )

    doc_notebooks = sorted(glob.glob("{}/*.ipynb".format(doc_notebooks_dir)))
    c.run(
        "jupyter nbconvert --to rst {} --output-dir={}/notebooks".format(
            " ".join(doc_notebooks), doc_dir_name
        )
    )
    toc_nbs = [
        "   notebooks/{}".format(np.split("/")[-1].split(".")[0])
        for np in doc_notebooks
    ]

    index_rst = """
Welcome to {}'s documentation!
=====================================================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   autosumm
{}
   {}

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
""".format(
        package_name, "\n".join(toc_nbs), "release_notes/main"
    )

    autosumm_rst = """

API
===

.. automodapi:: {}

""".format(
        package_name
    )

    with open(os.path.join(doc_dir_name, "index.rst"), "w") as fp:
        fp.write(index_rst)

    with open(os.path.join(doc_dir_name, "autosumm.rst"), "w") as fp:
        fp.write(autosumm_rst)

    c.run("cp -r docs_config/* docs/")
    c.run("pip install -r docs/requirements.txt")
    c.run("sphinx-build docs docs/_build")
