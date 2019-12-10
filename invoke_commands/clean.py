from invoke import task

from .vars import package_name


@task
def clean(
    c, docs=False, build=False, bytecode=False, test=False, sonar=False, all=False
):
    patterns = []
    if docs or all:
        patterns.append("docs")
    if build or all:
        patterns += ["build", "{}.egg-info".format(package_name)]
    if bytecode or all:
        patterns.append("**/*.pyc")
    if sonar or all:
        patterns += [
            "{}/.sonar".format(package_name),
            "{}/.scannerwork".format(package_name),
            "{}/sonar-project.properties".format(package_name),
        ]
    if test or all:
        patterns += [
            ".pytest_cache",
            ".coverage",
            "**/.coverage",
            "htmlcov",
            "**/coverage.xml",
        ]

    for pattern in patterns:
        c.run("rm -rf {}".format(pattern))


@task
def prune(c):
    clean(c, all=True)
