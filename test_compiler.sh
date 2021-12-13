#!/bin/bash

BASE="$(pwd)/test_codegen_v2/test_codegen/"
TARGET=$1
INPUT_NAME="${BASE}${TARGET}.fl"
EXPECTED_NAME="${BASE}${TARGET}.expected"

echo ".....testing $INPUT_NAME"

python -m src.parser $INPUT_NAME > "$INPUT_NAME.ast"

python -m src.compiler "$INPUT_NAME.ast" > "$INPUT_NAME.mam"

"./mamarracho.bin" "$INPUT_NAME.mam" > "$INPUT_NAME.eval"

diff "$INPUT_NAME.eval" "$EXPECTED_NAME"

if [ $? != 0 ]
then
    echo "test: $TARGET failed"
fi
