from invoke import task
from invoke.exceptions import UnexpectedExit

from .vars import package_name

DJANGO_PROJECT_NAME = "dev_project"


@task
def setup_dev(c):
    host_ip = "0.0.0.0"
    app_port = 6969
    c.run(
        f"APP_NAME={package_name} "
        f"DJANGO_PROJECT={DJANGO_PROJECT_NAME} "
        f"HOST_IP={host_ip} "
        f"APP_PORT={app_port} "
        "docker-compose up --build"
    )


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
