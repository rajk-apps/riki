# 

This is a python package template

## what to modify:

- the mypackage folder name and its contents
- the notebooks folder contents
- conftest.py
- the pyproject.toml
  - make sure the name here matches the modified folder name of mypackage, otherwise 
  some other things need to be modified too
- requirements.txt
- README.md
- docs_config/release_notes

## use invoke:

#### release cycle
- build
  - docs too
- test
  - ```inv test```, ```inv test --option=whatever```, ```inv test --xml```

- publish
  - ```inv new-release``` only if twine is configured

- deploy
  - set something for this


#### analytics

- sonar


## get badges:

- from readthediocs, like this:

[![Documentation Status](https://readthedocs.org/projects/mypackage/badge/?version=latest)](https://jelm.readthedocs.io/en/mypackage/?badge=latest)

- from codecov, somehow

- from some ci somehow


## start a new package using this thing:

```git clone something```


## todo:

- make starting script
- put notebooks to test
- solve the stupid sys path append issue with the notebooks
- add build if cython is present, toml (invoke?) for build reqs
- check requirements


## set as remote for updates:

```git remote add boilerplate git@github.com:endremborza/python_boilerplate.git```
```git fetch boilerplate```
```git merge boilerplate/master --allow-unrelated-histories``` if end is needed
```git checkout --ours / --theirs for conflicts```