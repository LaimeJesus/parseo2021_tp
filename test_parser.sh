#!/bin/bash

BASE="$(pwd)/tests_parser/"
TARGET=$1
INPUT_NAME="${BASE}${TARGET}.input"
OUTPUT_NAME="${BASE}${TARGET}.output"
EXPECTED_NAME="${BASE}${TARGET}.expected"

echo ".....testing $INPUT_NAME"

python -m src.parser $INPUT_NAME > $OUTPUT_NAME

diff "$OUTPUT_NAME" "$EXPECTED_NAME"

if [ $? != 0 ]
then
    echo "test: $TARGET failed"
fi
