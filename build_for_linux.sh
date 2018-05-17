#!/usr/bin/env bash

cd "$(dirname "${BASH_SOURCE[0]}")"
. env/bin/activate

echo "--------------------------------------------------"
echo "Remove dirs"
rm -rf build dist

echo "--------------------------------------------------"
echo "Compile GUI"
pyinstaller ./memority/memority_gui.pyw --name "Memority UI" --windowed --icon=img/icon.ico

echo "--------------------------------------------------"
echo "Compile Core"
pyinstaller ./memority/memority_core_systray.pyw --name "Memority Core" --hidden-import cytoolz.utils --hidden-import cytoolz._signatures --hidden-import raven.handlers --hidden-import raven.handlers.logging --hidden-import sqlalchemy.ext.baked --additional-hooks-dir=pyinstaller-hooks --windowed --icon=img/icon.ico


echo "--------------------------------------------------"
echo "Add files to build"
mkdir -p dist/memority/DEBIAN
mkdir -p dist/memority/usr/lib/memority
mkdir -p dist/memority/usr/share/pixmaps
mkdir -p dist/memority/usr/share/applications/
cp -r dist/Memority\ Core/* dist/memority/usr/lib/memority/
cp -r dist/Memority\ UI/* dist/memority/usr/lib/memority/
mkdir dist/memority/usr/lib/memority/settings
mkdir dist/memority/usr/lib/memority/smart_contracts
mkdir dist/memority/usr/lib/memority/geth
cp memority/settings/defaults.yml dist/memority/usr/lib/memority/settings/
cp -r memority/ui dist/memority/usr/lib/memority/
cp img/icon.ico dist/memority/usr/lib/memority/
cp -r memority/smart_contracts/binaries dist/memority/usr/lib/memority/smart_contracts/
cp -r memority/smart_contracts/install dist/memority/usr/lib/memority/smart_contracts/
cp memority/geth/linux/geth dist/memority/usr/lib/memority/geth/

cp dist-utils/control dist/memority/DEBIAN
cp dist-utils/postinst dist/memority/DEBIAN
cp dist-utils/memority-core.desktop dist/memority/usr/share/applications/
cp dist-utils/memority-ui.desktop dist/memority/usr/share/applications/
cp img/icon.ico dist/memority/usr/share/pixmaps/memority_icon.ico

echo "--------------------------------------------------"
echo "Building package"
fakeroot dpkg-deb --build dist/memority
