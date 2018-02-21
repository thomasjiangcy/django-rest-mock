import os
import shutil
import subprocess
import sys


def main(index_file):
    # Check if node is installed
    try:
        subprocess.check_output(['node', '-v'])
    except:
        sys.stdout.write('Node.js not installed properly.\n')
        sys.exit(0)

    # Check if Express is installed
    try:
        subprocess.check_output(['npm', 'list', 'express'])
    except:
        subprocess.call(['npm', 'install', 'express'])

    try:
        subprocess.call(["node", index_file])
    except KeyboardInterrupt:
        os.remove(index_file)
        path_prefix = os.getcwd()
        os.remove(path_prefix + '/package-lock.json')
        shutil.rmtree(path_prefix + '/node_modules')
        sys.stdout.write('Mock server shutdown.\n')
