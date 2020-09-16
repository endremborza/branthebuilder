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
        f"docker exec -i {package_name}_devcont_1 "
        f"python /{DJANGO_PROJECT_NAME}/manage.py "
        f"dumpdata {package_name} auth.user "
        "--indent=2 > dev_env/test_data/test_data_dump.json",
        "docker exec -i {}_devcont_1 rm -rf /{}/{}/migrations".format(
            package_name, DJANGO_PROJECT_NAME, package_name
        ),
        f"docker kill {package_name}_devcont_1",
        f"docker container rm {package_name}_devcont_1",
        f"mkdir {package_name}/migrations",
        f"touch {package_name}/migrations/__init__.py",
    ]

    for comm in cleaning_commands:
        try:
            c.run(comm)
        except UnexpectedExit:
            print(f"command failed: {comm}")


@task
def nb(c):

    c.run(f"docker exec -i {package_name}_devcont_1 pip install jupyter")
    c.run(
        f"docker exec -i {package_name}_devcont_1 "
        f"python /{DJANGO_PROJECT_NAME}/manage.py shell_plus --notebook"
    )
