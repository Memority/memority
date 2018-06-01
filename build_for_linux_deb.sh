#!/usr/bin/env bash

cd "$(dirname "${BASH_SOURCE[0]}")"
. env/bin/activate

VERSION=$1

echo "--------------------------------------------------"
echo "Remove dirs"
rm -rf build dist

echo "--------------------------------------------------"
echo "Compile"
pyinstaller ./memority/memority_gui.pyw \
--name "memority" \
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
mkdir -p dist/dist/memority/DEBIAN
mkdir -p dist/dist/memority/usr/lib/memority
mkdir -p dist/dist/memority/usr/share/pixmaps
mkdir -p dist/dist/memority/usr/share/applications/
mkdir dist/dist/memority/usr/lib/memority/settings
mkdir dist/dist/memority/usr/lib/memority/smart_contracts
mkdir dist/dist/memority/usr/lib/memority/geth
cp memority/settings/defaults.yml dist/dist/memority/usr/lib/memority/settings/
cp memority/icon.ico dist/dist/memority/usr/lib/memority/
cp memority/splashscreen.jpg dist/dist/memority/usr/lib/memority/
cp memority/geth/linux/geth dist/dist/memority/usr/lib/memority/geth/
cp -r dist/memority/* dist/dist/memority/usr/lib/memority/
cp -r memority/ui dist/dist/memority/usr/lib/memority/
cp -r memority/smart_contracts/binaries dist/dist/memority/usr/lib/memority/smart_contracts/
cp -r memority/smart_contracts/install dist/dist/memority/usr/lib/memority/smart_contracts/

echo "Package: memority
Version: ${VERSION}
Section: misc
Architecture: amd64
Maintainer: A. Vityk <andrii.vityk@gmail.com>
Description: Blockchain Based Data Storage
 Memority is a blockchain-based platform for encrypted decentralized cloud storage of valuable data.
" > dist/dist/memority/DEBIAN/control

cp dist-utils/postinst dist/dist/memority/DEBIAN

echo "[Desktop Entry]
Encoding=UTF-8
Version=${VERSION}
Type=Application
Terminal=false
Exec=/usr/lib/memority/memority
Name=Memority
Icon=/usr/share/pixmaps/memority_icon.png
" > dist/dist/memority/usr/share/applications/memority.desktop

cp img/icon.png dist/dist/memority/usr/share/pixmaps/memority_icon.png

echo "--------------------------------------------------"
echo "Building package"
fakeroot dpkg-deb --build dist/dist/memority
mv dist/dist/memority.deb Memority-v${VERSION}-linux-setup.deb
