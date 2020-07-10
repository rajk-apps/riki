from invoke import task
from invoke.exceptions import UnexpectedExit

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

    cleaning_commands = [
        "docker exec -i {}_devcont_1 python /{}/manage.py dumpdata {} auth.user".format(
            package_name, DJANGO_PROJECT_NAME, package_name
        )
        + " --indent=2 > dev_env/test_data/test_data_dump.json",
        "docker exec -i {}_devcont_1 rm -rf /{}/{}/migrations".format(
            package_name, DJANGO_PROJECT_NAME, package_name
        ),
        "docker kill {}_devcont_1".format(package_name),
        "docker container rm {}_devcont_1".format(package_name),
        "mkdir {}/migrations".format(package_name),
        "touch {}/migrations/__init__.py".format(package_name),
    ]

    for comm in cleaning_commands:
        try:
            c.run(comm)
        except UnexpectedExit:
            print("command failed: {}".format(comm))


@task
def nb(c):

    c.run(f"docker exec -i {package_name}_devcont_1 pip install jupyter")
    c.run(
        f"docker exec -i {package_name}_devcont_1 python /{DJANGO_PROJECT_NAME}/manage.py shell_plus --notebook"
    )
