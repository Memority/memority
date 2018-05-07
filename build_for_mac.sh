#!/usr/bin/env bash

cd "$(dirname "${BASH_SOURCE[0]}")"

. env/bin/activate

echo "--------------------------------------------------"
echo "Remove dirs"
rm -rf build dist

echo "--------------------------------------------------"
echo "Compile GUI"
pyinstaller ./memority/gui/memority_gui.pyw --name "Memority UI" --windowed --icon=img/memority_icon_256.icns

echo "--------------------------------------------------"
echo "Compile Core"
pyinstaller ./memority/memority_core/memority_core_systray.pyw --name "Memority Core" --hidden-import cytoolz.utils --hidden-import cytoolz._signatures --hidden-import raven.handlers --hidden-import raven.handlers.logging --hidden-import sqlalchemy.ext.baked --additional-hooks-dir=pyinstaller-hooks --windowed --icon=img/memority_icon_256.icns

echo "--------------------------------------------------"
echo "Add files to build"
mkdir dist/Memority\ UI.app/Contents/MacOS/settings
cp memority/gui/settings/defaults.yml dist/Memority\ UI.app/Contents/MacOS/settings

mkdir dist/Memority\ Core.app/Contents/MacOS/settings
mkdir dist/Memority\ Core.app/Contents/MacOS/smart_contracts
mkdir dist/Memority\ Core.app/Contents/MacOS/geth
cp img/icon.ico dist/Memority\ Core.app/Contents/MacOS
cp memority/memority_core/settings/defaults.yml dist/Memority\ Core.app/Contents/MacOS/settings
cp -r memority/memority_core/smart_contracts/binaries dist/Memority\ Core.app/Contents/MacOS/smart_contracts
cp -r memority/memority_core/smart_contracts/binaries dist/Memority\ Core.app/Contents/MacOS/smart_contracts
cp -r memority/memority_core/smart_contracts/install dist/Memority\ Core.app/Contents/MacOS/smart_contracts
cp memority/memority_core/geth/darwin/geth dist/Memority\ Core.app/Contents/MacOS/geth

rm -rf dist/Memority\ Core dist/Memority\ UI
mkdir dist/core dist/ui
mv dist/Memority\ Core.app dist/core/Memority\ Core.app
mv dist/Memority\ UI.app dist/ui/Memority\ UI.app

echo "--------------------------------------------------"
echo "Building package"

VERSION=$1

sed 's/version=\"\"/version=\"'"${VERSION}"'\"/g' dist-utils/Distribution.xml > ./dist/Distribution.xml
pkgbuild --install-location /Applications/Memority --root dist/core --version "${VERSION}" --component-plist ./dist-utils/MemorityCoreComponents.plist --identifier io.memority.memoritycore ./dist/Memority\ Core.pkg
pkgbuild --install-location /Applications/Memority --root dist/ui --version "${VERSION}" --component-plist ./dist-utils/MemorityUIComponents.plist --identifier io.memority.memorityui ./dist/Memority\ UI.pkg
productbuild --distribution ./dist/Distribution.xml --package-path ./dist --resources . "./Memority-${VERSION}-macos-setup.pkg"

echo "--------------------------------------------------"
echo "Cleanup"

rm -rf build dist *.spec

echo "Done!"
