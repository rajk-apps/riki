from invoke import task

from .vars import package_name, boilerplate_branch

DJANGO_PROJECT_NAME = "dev_project"


@task
def setup_dev(c):
    c.run(
        "APP_NAME={} ".format(package_name)
        + "DJANGO_PROJECT={} ".format(DJANGO_PROJECT_NAME)
        + "HOST_IP={} ".format("0.0.0.0")  # FIXME: is this dry?
        + "APP_PORT={} ".format(6969)
        + "docker-compose up --build"
    )  # -- build


@task
def clean(c):
    c.run(
        "docker exec -i {}_devcont_1 python /{}/manage.py dumpdata {}".format(
            package_name, DJANGO_PROJECT_NAME, package_name
        )
        + " --indent=2 > dev_env/test_data/test_data_dump.json"
    )
    c.run(
        "docker exec -i {}_devcont_1 rm -rf /{}/{}/migrations".format(
            package_name, DJANGO_PROJECT_NAME, package_name
        )
    )
    c.run("docker kill {}_devcont_1".format(package_name))
    c.run("docker container rm {}_devcont_1".format(package_name))
    c.run("mkdir {}/migrations".format(package_name))
    c.run("touch {}/migrations/__init__.py".format(package_name))
