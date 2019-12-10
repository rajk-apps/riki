import io
from invoke import task

from .vars import mymodule


@task
def new(c):

    version = mymodule.__version__

    f = io.StringIO()
    c.run("git rev-parse --abbrev-ref HEAD", out_stream=f)
    branch = f.getvalue().strip()
    f.close()

    if branch == "master":
        tag_version = "v{}".format(version)
        f2 = io.StringIO()
        c.run("git tag", out_stream=f2)
        tags = f2.getvalue().split()
        print(tags)
        if tag_version not in tags:
            with open("docs_config/current_release.rst") as fp:
                notes = fp.read()
            # TODO: remove this file, move to rlease_notes, and add to the end of main.rst
            c.run("git tag -a {} -m {}".format(tag_version, notes))
            c.run("python setup.py sdist")
            c.run("twine check dist/*")
            c.run("twine upload dist/*{}.tar.gz".format(version))
        else:
            print("{} version already tagged".format(tag_version))
    else:
        print("only master branch can be tagged")
