#!/usr/bin/env bash

cd "$(dirname "${BASH_SOURCE[0]}")"

. env/bin/activate

echo "--------------------------------------------------"
echo "Remove dirs"
rm -rf build dist

echo "--------------------------------------------------"
echo "Build"
pyinstaller ./memority/memority_gui.pyw \
--name "Memority" \
--hidden-import celery.fixups \
--hidden-import celery.backends \
--hidden-import celery.backends.base \
--hidden-import celery.loaders.app \
--hidden-import celery.app.amqp \
--hidden-import celery.app.events \
--hidden-import kombu.transport.sqlalchemy \
--hidden-import celery.fixups.django \
--hidden-import cytoolz.utils \
--hidden-import cytoolz._signatures \
--hidden-import raven.handlers \
--hidden-import raven.handlers.logging \
--hidden-import sqlalchemy.ext.baked \
--additional-hooks-dir=pyinstaller-hooks \
--windowed \
--icon=img/memority_icon_256.icns

echo "--------------------------------------------------"
echo "Add files to build"
mkdir dist/Memority.app/Contents/MacOS/models
mkdir dist/Memority.app/Contents/MacOS/settings
mkdir dist/Memority.app/Contents/MacOS/smart_contracts
mkdir dist/Memority.app/Contents/MacOS/geth

cp memority/settings/defaults.yml dist/Memority.app/Contents/MacOS/settings
cp -r memority/ui dist/Memority.app/Contents/MacOS/
cp memority/icon.ico dist/Memority.app/Contents/MacOS
cp memority/splashscreen.jpg dist/Memority.app/Contents/MacOS
cp memority/smart_contracts/contracts.json dist/Memority.app/Contents/MacOS/smart_contracts
cp -r memority/smart_contracts/binaries dist/Memority.app/Contents/MacOS/smart_contracts
cp -r memority/smart_contracts/install dist/Memority.app/Contents/MacOS/smart_contracts
cp -r memority/models/db_migrations dist/Memority.app/Contents/MacOS/models
cp memority/geth/darwin/geth dist/Memority.app/Contents/MacOS/geth

rm -rf dist/Memority
mkdir dist/dist
mv dist/Memority.app dist/dist/Memority.app

echo "--------------------------------------------------"
echo "Building package"

VERSION=$1

sed 's/version=\"\"/version=\"'"${VERSION}"'\"/g' dist-utils/Distribution.xml > ./dist/Distribution.xml
pkgbuild --install-location /Applications/Memority --root dist/dist --version "${VERSION}" --component-plist ./dist-utils/MemorityComponents.plist --identifier io.memority.memority ./dist/Memority.pkg
productbuild --distribution ./dist/Distribution.xml --package-path ./dist --resources . "./dist/Memority-${VERSION}-macos-setup.pkg"
productsign --sign "Developer ID Installer" "./dist/Memority-${VERSION}-macos-setup.pkg" "./Memority-${VERSION}-macos-setup.pkg"

echo "--------------------------------------------------"
echo "Cleanup"

rm -rf build dist *.spec

echo "Done!"
