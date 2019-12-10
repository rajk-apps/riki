from invoke import task

from .vars import package_name


@task
def test(c, option="", html=False, xml=False):

    comm = "python -m pytest --cov={}".format(package_name)
    if option:
        comm += " --{}".format(option)
    if html:
        comm += " --cov-report=html"
    elif xml:
        comm += " --cov-report=xml:{}/coverage.xml".format(package_name)

    c.run(comm)
