import os
import subprocess
import sys


def main(index_file):
    # Check if node is installed
    node_exists = subprocess.check_output(['node', '-v'])
    if not node_exists:
        sys.stdout.write('Node installation not found. Please install Node.js')
        sys.exit(0)

    # Check if Express is installed
    try:
        express_exists = subprocess.check_output(['npm', 'list', '-g', 'express'])
    except subprocess.CalledProcessError:
        sys.stdout.write('Express installation not found globally, checking local npm installation...')

        try:
            express_exists = subprocess.check_output(['npm', 'list', 'express'])
        except subprocess.CalledProcessError:
            sys.stdout.write('Express installation not found locally. Please ensure Express is installed')
            sys.exit(0)


    try:
        subprocess.call(["node", index_file])
    except KeyboardInterrupt:
        os.remove(index_file)
        sys.stdout.write('Mock server shutdown.')
