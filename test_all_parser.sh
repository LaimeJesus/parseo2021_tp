#!/bin/bash

tests=(
    "test00"
    "test01"
    "test02"
    "test03"
    "test04"
    "test05"
    "test06"
    "test07"
    "test08"
    "test09"
    "test10"
    "test11"
    "test12"
    "test13"
    "test14"
    "test15"
    "test16"
    "test17"
    "test18"
)

for test in "${tests[@]}"; do
    bash "test_parser.sh" $test
done
