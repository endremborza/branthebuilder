from invoke import task
from invoke.exceptions import UnexpectedExit

from .vars import conf

DJANGO_PROJECT_NAME = "dev_project"


@task
def setup_dev(c):
    host_ip = "0.0.0.0"
    app_port = 6969
    c.run(
        f"APP_NAME={conf.name} "
        f"DJANGO_PROJECT={DJANGO_PROJECT_NAME} "
        f"HOST_IP={host_ip} "
        f"APP_PORT={app_port} "
        "docker-compose up --build"
    )


@task
def clean(c):

    cleaning_commands = [
        f"docker exec -i {conf.name}_devcont_1 "
        f"python /{DJANGO_PROJECT_NAME}/manage.py "
        f"dumpdata {conf.name} auth.user "
        "--indent=2 > dev_env/test_data/test_data_dump.json",
        "docker exec -i {}_devcont_1 rm -rf /{}/{}/migrations".format(
            conf.name, DJANGO_PROJECT_NAME, conf.name
        ),
        f"docker kill {conf.name}_devcont_1",
        f"docker container rm {conf.name}_devcont_1",
        f"mkdir {conf.name}/migrations",
        f"touch {conf.name}/migrations/__init__.py",
    ]

    for comm in cleaning_commands:
        try:
            c.run(comm)
        except UnexpectedExit:
            print(f"command failed: {comm}")


@task
def nb(c):

    c.run(f"docker exec -i {conf.name}_devcont_1 pip install jupyter")
    c.run(
        f"docker exec -i {conf.name}_devcont_1 "
        f"python /{DJANGO_PROJECT_NAME}/manage.py shell_plus --notebook"
    )
