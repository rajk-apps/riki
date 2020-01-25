from invoke import task
from .vars import package_name, boilerplate_branch


@task
def lint(c):
    c.run("black . --exclude \.*venv".format(package_name))
    c.run("flake8 {}".format(package_name))


@task
def update_boilerplate(c):  # TODO: maybe drop template package folder
    c.run("git fetch boilerplate")  # TODO: this knows the name of the remote
    c.run("git merge boilerplate/{} --no-edit".format(boilerplate_branch))


@task
def notebook(c):
    c.run("python invoke_commands/notebook_runner.py")
