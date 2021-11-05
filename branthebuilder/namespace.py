from invoke import Collection

from . import django, docs, release, sonar
from .clean import clean, purge
from .misc import lint, notebook, update_boilerplate
from .test import test

ns = Collection()
for module in [docs, sonar, release, django]:
    ns.add_collection(Collection.from_module(module))

for task in [lint, test, notebook, clean, purge, update_boilerplate]:
    ns.add_task(task)
