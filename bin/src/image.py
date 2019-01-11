from src import bcolors
import docker
from yaspin import yaspin


def _setup_python2(container):

    with yaspin(text="Updating container....", color="green") as spinner:
        container.exec_run('apt update')
        container.exec_run('apt upgrade')
        spinner.ok("✔")

    with yaspin(text="Installing python2.7", color="green") as spinner:
        container.exec_run('apt install -y python2.7')
        container.exec_run('apt install -y python-minimal')
        spinner.ok("✔")

    with yaspin(text="Installing pip", color="green") as spinner:
        container.exec_run('apt install -y python-pip')
        spinner.ok("✔")


def setup_image(enviornment, micobox_image, image_identifier):
    if enviornment not in ['python3', 'python2']:
        print(bcolors.WARNING + 'Invalid environment!' + bcolors.ENDC)
        return False

    client = docker.from_env()

    print(bcolors.HEADER + 'This is the first time hence will take some time. Other installtions will be fast!'
          + bcolors.ENDC)

    with yaspin(text="Initializing Container....", color="green") as spinner:
        container = client.containers.run('ubuntu', '/bin/sh -c "while true; do ping 8.8.8.8; done"', detach=True)
        spinner.ok("✔")

    if enviornment == 'python2':
        _setup_python2(container)

    with yaspin(text="Finalizing Container....", color="green") as spinner:
        container.pause()
        container.commit(repository=image_identifier)
        container.kill()
        container.remove()
        spinner.ok("✔")

    return True
