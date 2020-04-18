import os
import glob
import json
from invoke import task

from .vars import package_name, doctest_notebooks_glob


@task
def test(c, option="", html=False, xml=False, notebook_tests=True):

    comm = f"python -m pytest --cov={package_name}"
    if option:
        comm += f" --{option}"
    if html:
        comm += " --cov-report=html"
    elif xml:
        comm += f" --cov-report=xml:{package_name}/coverage.xml"

    if notebook_tests:
        new_test_scripts = []
        for nb_idx, nb_file in enumerate(glob.glob(doctest_notebooks_glob)):
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
                    f"def test_nb_integration_{nb_idx}():\n"
                    + "\n".join([f"    {s}" for s in nb_code.split("\n")])
                )

        test_root = os.path.join(package_name, "tests")
        if not os.path.exists(test_root):
            os.makedirs(test_root)

        test_notebook_path = os.path.join(test_root, "test_nb_integrations.py")
        with open(test_notebook_path, "w") as fp:
            fp.write("\n\n".join(new_test_scripts))

    c.run(comm)
    c.run("rm {}/tests/test_nb_integrations.py".format(package_name))
