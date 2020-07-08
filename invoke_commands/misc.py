from invoke import task
from .vars import package_name, boilerplate_branch


@task
def lint(c):
    c.run("black . -l 79 --exclude \.*venv")
    c.run(f"isort -rc {package_name} -m 3 -tc")
    c.run(f"flake8 {package_name}")


@task
def update_boilerplate(c):  # TODO: maybe drop template package folder
    c.run("git fetch boilerplate")  # TODO: this knows the name of the remote
    c.run(f"git merge boilerplate/{boilerplate_branch} --no-edit")


@task
def notebook(c):
    c.run("python invoke_commands/notebook_runner.py")
