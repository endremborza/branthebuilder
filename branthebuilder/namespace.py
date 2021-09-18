from invoke import Collection

from . import clean, django, docs, release, sonar, test
from .misc import lint, notebook, update_boilerplate

ns = Collection()
for module in [docs, clean, sonar, test, release, django]:
    ns.add_collection(Collection.from_module(module))

for task in [lint, notebook, update_boilerplate]:
    ns.add_task(task)
