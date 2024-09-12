#!/usr/bin/env bash

set -o errexit # Exit if command failed
set -o pipefail # Exit if pipe failed
set -o nounset # Exit if variable not set

DEFAULT_FUNCTION="main"

# Check the number of arguments
if [ $# -eq 0 ]; then
    echo "Error: Not enough arguments. Specify the file to dump." >&2
    exit 1
elif [ $# -eq 1 ]; then
    FILE=$1
    FUNCTION=$DEFAULT_FUNCTION
elif [ $# -eq 2 ]; then
    FILE=$1
    FUNCTION=$2
else
    echo "Error: Too many arguments provided."
    exit 1
fi

DUMP_RAW=$(gdb -batch -ex "set disassembly-flavor intel" -ex "file $FILE" -ex "disassemble $FUNCTION")
DUMP_CLEANED=$(echo "$DUMP_RAW" | head -n-1 | tail -n+2 | sed -r 's/\s+/\t/g' | cut  -f2-)

echo "$DUMP_CLEANED"