import random
import string
import subprocess
import os
import yaml
import uuid
import io
from src import bcolors
from src.image import setup_image
from yaspin import yaspin


def run_container():
    if not os.path.exists(os.getcwd() + '/box.yaml'):
        print(bcolors.WARNING + 'No box.yaml file found!' + bcolors.ENDC)
        return

    with open("box.yaml", 'r') as stream:
        try:
            boxyaml = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(bcolors.WARNING + 'Invalid box.yaml' + bcolors.ENDC)
            print(exc)

    if 'environment' not in boxyaml:
        print(bcolors.WARNING + 'No environment found in box.yaml' + bcolors.ENDC)
        return

    environment = boxyaml['environment']

    if 'identifier' in boxyaml:
        image_identifier = boxyaml['identifier']
    else:
        image_identifier = str(uuid.uuid4().hex)
        boxyaml['identifier'] = image_identifier
        with io.open('box.yaml', 'w', encoding='utf8') as outfile:
            yaml.dump(boxyaml, outfile, default_flow_style=False, allow_unicode=True)

    FNULL = open(os.devnull, 'w')
    container_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    image_exist = subprocess.check_output(['docker', 'images', '-q', image_identifier])

    if not image_exist:
        microbox_image = 'ubuntu'
        if not setup_image(environment, microbox_image, image_identifier):
            print(bcolors.WARNING + 'Cannot setup base image!' + bcolors.ENDC)
            return
    else:
        microbox_image = image_identifier

    print(bcolors.OKGREEN + 'Logging you in....' + bcolors.ENDC)
    subprocess.call(['docker', 'run', '-w', '/root/app', '-it', '--name', container_name,
                     '-v', '{0}/:/root/app'.format(os.getcwd()), microbox_image, '/bin/bash'])

    with yaspin(text="Pausing container....", color="green") as spinner:
        container_id = subprocess.check_output(['docker', 'ps', '-aqf', "name={0}".format(container_name)])
        container_id = str(container_id.decode("utf-8")).strip()

        subprocess.call(['docker', 'commit', container_id, image_identifier], stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call(['docker', 'rm', container_id], stdout=FNULL, stderr=subprocess.STDOUT)

        spinner.ok('✔')
