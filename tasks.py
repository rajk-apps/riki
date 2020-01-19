from invoke import Collection

ns = Collection()
ns.add_collection(Collection.from_module(release))
ns.add_collection(Collection.from_module(docs))
ns.add_collection(Collection.from_module(clean))
ns.add_collection(Collection.from_module(sonar))
ns.add_collection(Collection.from_module(test))
ns.add_collection(Collection.from_module(django))
ns.add_collection(Collection.from_module(misc))