from invoke import task, Collection

from invoke_commands import docs, clean, sonar, test, release, django

from invoke_commands.vars import package_name


@task
def lint(c):
    c.run("black {}".format(package_name))
    c.run("flake8 {}".format(package_name))


ns = Collection()
ns.add_collection(Collection.from_module(release))
ns.add_collection(Collection.from_module(docs))
ns.add_collection(Collection.from_module(clean))
ns.add_collection(Collection.from_module(sonar))
ns.add_collection(Collection.from_module(test))
ns.add_collection(Collection.from_module(django))
