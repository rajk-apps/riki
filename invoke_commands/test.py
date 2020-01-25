import glob
import json
from invoke import task

from .vars import package_name, doc_notebooks_dir


@task
def test(c, option="", html=False, xml=False, notebook_tests=True):

    comm = "python -m pytest --cov={}".format(package_name)
    if option:
        comm += " --{}".format(option)
    if html:
        comm += " --cov-report=html"
    elif xml:
        comm += " --cov-report=xml:{}/coverage.xml".format(package_name)

    if notebook_tests:
        new_test_scripts = []
        for nb_idx, nb_file in enumerate(
            glob.glob("{}/*.ipynb".format(doc_notebooks_dir))
        ):
            nb_dic = json.load(open(nb_file))
            nb_code = "\n".join(
                [
                    "\n".join(c["source"])
                    for c in nb_dic["cells"]
                    if (c["cell_type"] == "code")
                ]
            )
            if len(nb_code) > 0:
                new_test_scripts.append(
                    "def test_nb_integration_{}():\n".format(nb_idx)
                    + "\n".join(["    {}".format(s) for s in nb_code.split("\n")])
                )
        with open("{}/tests/test_nb_integrations.py".format(package_name), "w") as fp:
            fp.write("\n\n".join(new_test_scripts))

    c.run(comm)
    c.run("rm {}/tests/test_nb_integrations.py".format(package_name))
