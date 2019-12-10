from invoke import task

from .vars import package_name


@task
def setup_dev(c):
    c.run("APP_NAME={} " .format(package_name) +
          "DJANGO_PROJECT={} ".format("dev_project") +  # FIXME: is this dry?
          "HOST_IP={} ".format("0.0.0.0") +
          "APP_PORT={} ".format(6969) +
          "docker-compose up --build")  # -- build

@task
def clean(c):
    c.run("rm -{}/migrations/*".format(package_name))
