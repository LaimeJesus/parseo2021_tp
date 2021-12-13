#!/bin/bash

BASE="$(pwd)/test_codegen_v2/test_codegen/"
TARGET=$1
INPUT_NAME="${BASE}${TARGET}.fl.mam"
EXPECTED_NAME="${BASE}${TARGET}.expected"

echo ".....testing $INPUT_NAME"

"./mamarracho.bin" "$INPUT_NAME" > "$INPUT_NAME.eval"

diff "$INPUT_NAME.eval" "$EXPECTED_NAME"

if [ $? != 0 ]
then
    echo "test: $TARGET failed"
fi
