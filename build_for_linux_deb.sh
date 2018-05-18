#!/usr/bin/env bash

cd "$(dirname "${BASH_SOURCE[0]}")"
. env/bin/activate

VERSION=$1

echo "--------------------------------------------------"
echo "Remove dirs"
rm -rf build dist

echo "--------------------------------------------------"
echo "Compile GUI"
pyinstaller ./memority/memority_gui.pyw \
--name "memority-ui" \
--windowed \
--icon=img/icon.png

echo "--------------------------------------------------"
echo "Compile Core"
pyinstaller ./memority/memority_core_systray.pyw \
--name "memority-core" \
--hidden-import cytoolz.utils \
--hidden-import cytoolz._signatures \
--hidden-import raven.handlers \
--hidden-import raven.handlers.logging \
--hidden-import sqlalchemy.ext.baked \
--additional-hooks-dir=pyinstaller-hooks \
--windowed \
--icon=img/icon.png


echo "--------------------------------------------------"
echo "Add files to build"
mkdir -p dist/memority/DEBIAN
mkdir -p dist/memority/usr/lib/memority
mkdir -p dist/memority/usr/share/pixmaps
mkdir -p dist/memority/usr/share/applications/
mkdir dist/memority/usr/lib/memority/settings
mkdir dist/memority/usr/lib/memority/smart_contracts
mkdir dist/memority/usr/lib/memority/geth
cp memority/settings/defaults.yml dist/memority/usr/lib/memority/settings/
cp img/icon.ico dist/memority/usr/lib/memority/
cp memority/geth/linux/geth dist/memority/usr/lib/memority/geth/
cp -r dist/memority-core/* dist/memority/usr/lib/memority/
cp -r dist/memority-ui/* dist/memority/usr/lib/memority/
cp -r memority/ui dist/memority/usr/lib/memority/
cp -r memority/smart_contracts/binaries dist/memority/usr/lib/memority/smart_contracts/
cp -r memority/smart_contracts/install dist/memority/usr/lib/memority/smart_contracts/

echo "Package: memority
Version: ${VERSION}
Section: misc
Architecture: amd64
Maintainer: A. Vityk <andrii.vityk@gmail.com>
Description: Blockchain Based Data Storage
 Memority is a blockchain-based platform for encrypted decentralized cloud storage of valuable data.
" > dist/memority/DEBIAN/control

cp dist-utils/postinst dist/memority/DEBIAN

echo "[Desktop Entry]
Encoding=UTF-8
Version=${VERSION}
Type=Application
Terminal=false
Exec=/usr/lib/memority/memority-core
Name=Memority Core
Icon=/usr/share/pixmaps/memority_icon.png
" > dist/memority/usr/share/applications/memority-core.desktop

echo "[Desktop Entry]
Encoding=UTF-8
Version=${VERSION}
Type=Application
Terminal=false
Exec=/usr/lib/memority/Memority\\ UI
Name=Memority UI
Icon=/usr/share/pixmaps/memority_icon.png
" > dist/memority/usr/share/applications/memority-ui.desktop

cp img/icon.png dist/memority/usr/share/pixmaps/memority_icon.png

echo "--------------------------------------------------"
echo "Building package"
fakeroot dpkg-deb --build dist/memority
mv dist/memority.deb Memority-v${VERSION}-linux-setup.deb
