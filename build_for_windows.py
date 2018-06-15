import sys

import contextlib
import jinja2
import os
import shutil
import subprocess
import traceback


def makedirs(path):
    with contextlib.suppress(FileExistsError):
        os.makedirs(path)


def split(path):
    folders = []
    path, folder = os.path.split(path)
    folders.append(folder)
    if not path:
        return folders
    else:
        folders += split(path)
        return folders


def run_subprocess(args):
    p = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
        close_fds=False
    )

    while True:
        line = p.stdout.readline()
        if line:
            print(line.strip())
        else:
            break


def main():
    # region Remove dirs
    print('-' * 100)
    print('Remove dirs')
    if os.path.isdir('build'):
        shutil.rmtree('build')

    if os.path.isdir('dist'):
        shutil.rmtree('dist')
    # endregion

    # region Build
    print('-' * 100)
    print('Build')
    run_subprocess([
        'pyinstaller',
        os.path.join('memority', 'memority_gui.pyw'),
        '--name',  'Memority',
        '--hidden-import', 'celery.fixups',
        '--hidden-import', 'celery.fixups.django',
        '--hidden-import', 'cytoolz.utils',
        '--hidden-import', 'cytoolz._signatures',
        '--hidden-import', 'raven.handlers',
        '--hidden-import', 'raven.handlers.logging',
        '--hidden-import', 'sqlalchemy.ext.baked',
        '--additional-hooks-dir=pyinstaller-hooks',
        f'--icon={os.path.join("img", "icon.ico")}',
        '--windowed'
    ])
    # endregion

    # region Add files to build
    print('-' * 100)
    print('Add files to build')
    makedirs(os.path.join('dist', 'Memority', 'models'))
    makedirs(os.path.join('dist', 'Memority', 'settings'))
    makedirs(os.path.join('dist', 'Memority', 'smart_contracts'))
    makedirs(os.path.join('dist', 'Memority', 'geth'))

    shutil.copytree(
        os.path.join('memority', 'ui'),
        os.path.join('dist', 'Memority', 'ui'))
    shutil.copyfile(
        os.path.join('memority', 'icon.ico'),
        os.path.join('dist', 'Memority', 'icon.ico'))
    shutil.copyfile(
        os.path.join('memority', 'splashscreen.jpg'),
        os.path.join('dist', 'Memority', 'splashscreen.jpg'))
    shutil.copyfile(
        os.path.join('memority', 'settings', 'defaults.yml'),
        os.path.join('dist', 'Memority', 'settings', 'defaults.yml'))
    shutil.copyfile(
        os.path.join('memority', 'smart_contracts', 'contracts.json'),
        os.path.join('dist', 'Memority', 'smart_contracts', 'contracts.json'))
    shutil.copytree(
        os.path.join('memority', 'smart_contracts', 'install'),
        os.path.join('dist', 'Memority', 'smart_contracts', 'install'))
    shutil.copytree(
        os.path.join('memority', 'models', 'db_migrations'),
        os.path.join('dist', 'Memority', 'models', 'db_migrations'))
    shutil.copyfile(
        os.path.join('memority', 'geth', 'Windows', 'geth.exe'),
        os.path.join('dist', 'Memority', 'geth', 'geth.exe'))
    shutil.copyfile(
        os.path.join('dist-utils', 'win-openssl-libs', 'libeay32.dll'),
        os.path.join('dist', 'Memority', 'libeay32.dll'))
    shutil.copyfile(
        os.path.join('dist-utils', 'win-openssl-libs', 'libssl32.dll'),
        os.path.join('dist', 'Memority', 'libssl32.dll'))
    shutil.copyfile(
        os.path.join('dist-utils', 'win-openssl-libs', 'ssleay32.dll'),
        os.path.join('dist', 'Memority', 'ssleay32.dll'))
    # endregion

    # region Create nsi template
    print('-' * 100)
    print('Create nsi template')
    context = {
        "version": sys.argv[1],
        "build_files": [
            (
                os.path.join(*list(reversed(split(d)))[2:]) if list(reversed(split(d)))[2:] else '',
                [os.path.join(d, file) for file in files]
            ) for d, _, files
            in os.walk(os.path.join('dist', 'Memority'))
            if files
        ],
    }
    compiled = jinja2.Environment(
        loader=jinja2.FileSystemLoader('dist-utils')
    ).get_template('nsi_template.jinja2').render(context)

    with open('memority.nsi', 'w') as f:
        f.write(compiled)
    # endregion

    # region Make installer executable
    print('-' * 100)
    print('Make installer executable')
    run_subprocess(['C:\\Program Files (x86)\\NSIS\\makensis.exe', 'memority.nsi'])
    # endregion
    input('Press Enter to exit')


if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        traceback.print_exc()
        input('Press Enter to exit')
