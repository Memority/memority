#!/usr/bin/env bash

cd "$(dirname "${BASH_SOURCE[0]}")"

UIS=()
RC_NAMES=()

rm ../gui/uic_loaded/*.py || true
rm ../gui/uic_loaded/resources/*.py || true


for FILE in $(ls *.ui)
do
    OUT="../gui/uic_loaded/`echo "$FILE" | sed 's/\./_/g'`.py"
    pyuic5 "$FILE" -o "$OUT"
    UIS+=($OUT)
done

for FILE in $(ls *.qrc)
do
    OUT_RC_NAME=`echo "$FILE" | sed 's/\.q/_/g'`
    OUT_RC_PY="../gui/uic_loaded/resources/$OUT_RC_NAME.py"
    pyrcc5 "$FILE" -o "$OUT_RC_PY"
    RC_NAMES+=("$OUT_RC_NAME")
done

for FILE in ${UIS[@]}
do
    for RC in ${RC_NAMES[@]}
    do
        sed -i "s/import $RC/from .resources.$RC import */g" "$FILE"
    done
done

echo "Done."
