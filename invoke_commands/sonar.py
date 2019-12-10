import os
from invoke import task

from .vars import package_name


@task
def setup(c):
    c.run("docker run -d --name sonarqube -p 9000:9000 -p 9092:9092 sonarqube")


@task
def scan(c):

    with open(os.path.join(package_name, "sonar-project.properties"), "w") as fp:
        fp.write(
            "sonar.projectKey={}\n"
            "sonar.python.coverage.reportPaths=coverage.xml\n"
            "sonar.scm.disabled=true".format(package_name)
        )

    c.run(
        "docker run -e SONAR_HOST_URL={} "
        '--user="$(id -u):$(id -g)" '
        '-t -v "{}/{}:/usr/src" sonarsource/sonar-scanner-cli'.format(
            "http://172.17.0.2:9000", os.getcwd(), package_name
        )
    )


@task
def kill(c):
    c.run("docker kill sonarqube")
    c.run("docker container rm sonarqube")
