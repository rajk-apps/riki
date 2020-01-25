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
            current_release_path = "docs_config/current_release.rst"
            with open(current_release_path) as fp:
                notes = fp.read()
            with open(
                "docs_config/release_notes/{}.rst".format(tag_version), "w"
            ) as fp:
                fp.write(notes)
            c.run("git tag -a {} -m {}".format(tag_version, notes))
            c.run("python setup.py sdist")
            c.run("twine check dist/*")
            c.run("twine upload dist/*{}.tar.gz".format(version))
            with open(current_release_path, "w") as fp:
                fp.write("")
        else:
            print("{} version already tagged".format(tag_version))
    else:
        print("only master branch can be tagged")
