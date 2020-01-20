from invoke import Collection

from invoke_commands import docs, clean, sonar, test, release, misc, django


ns = Collection()
ns.add_collection(Collection.from_module(release))
ns.add_collection(Collection.from_module(docs))
ns.add_collection(Collection.from_module(clean))
ns.add_collection(Collection.from_module(sonar))
ns.add_collection(Collection.from_module(test))
ns.add_collection(Collection.from_module(misc))
ns.add_collection(Collection.from_module(django))
