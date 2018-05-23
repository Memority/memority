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

    # region Compile
    print('-' * 100)
    print('Compile GUI')
    run_subprocess([
        'pyinstaller',
        os.path.join('memority', 'memority_gui.pyw'),
        f'--icon={os.path.join("img", "icon.ico")}',
        '--windowed'
    ])

    print('-' * 100)
    print('Compile Core')
    run_subprocess([
        'pyinstaller',
        os.path.join('memority', 'memority_core_systray.pyw'),
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
    makedirs(os.path.join('dist', 'memority_gui', 'settings'))
    shutil.copyfile(
        os.path.join('memority', 'settings', 'defaults.yml'),
        os.path.join('dist', 'memority_gui', 'settings', 'defaults.yml'))
    shutil.copytree(
        os.path.join('memority', 'ui'),
        os.path.join('dist', 'memority_gui', 'ui'))

    makedirs(os.path.join('dist', 'memority_core_systray', 'settings'))
    makedirs(os.path.join('dist', 'memority_core_systray', 'smart_contracts'))
    makedirs(os.path.join('dist', 'memority_core_systray', 'geth'))
    shutil.copyfile(
        os.path.join('img', 'icon.ico'),
        os.path.join('dist', 'memority_core_systray', 'icon.ico'))
    shutil.copyfile(
        os.path.join('memority', 'settings', 'defaults.yml'),
        os.path.join('dist', 'memority_core_systray', 'settings', 'defaults.yml'))
    shutil.copytree(
        os.path.join('memority', 'smart_contracts', 'binaries'),
        os.path.join('dist', 'memority_core_systray', 'smart_contracts', 'binaries'))
    shutil.copytree(
        os.path.join('memority', 'smart_contracts', 'install'),
        os.path.join('dist', 'memority_core_systray', 'smart_contracts', 'install'))
    shutil.copyfile(
        os.path.join('memority', 'geth', 'Windows', 'geth.exe'),
        os.path.join('dist', 'memority_core_systray', 'geth', 'geth.exe'))
    # endregion

    # region Create nsi template
    print('-' * 100)
    print('Create nsi template')
    context = {
        "version": sys.argv[1],
        "core_files": [
            (
                os.path.join('core', *list(reversed(split(d)))[2:]),
                [os.path.join(d, file) for file in files]
            ) for d, _, files
            in os.walk(os.path.join('dist', 'memority_core_systray'))
            if files
        ],
        "ui_files": [
            (
                os.path.join('ui', *list(reversed(split(d)))[2:]),
                [os.path.join(d, file) for file in files]
            ) for d, _, files
            in os.walk(os.path.join('dist', 'memority_gui'))
            if files
        ]
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
