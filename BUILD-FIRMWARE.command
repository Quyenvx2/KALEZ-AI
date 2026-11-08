#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="${0:A:h}"
PROJECT_DIR="$SCRIPT_DIR/source/xiaozhi-esp32"
IDF_EXPORT="${IDF_EXPORT:-/Users/huyvector/esp/v5.5.2/esp-idf/export.sh}"

if [[ ! -f "$IDF_EXPORT" ]]; then
  echo "Khong tim thay ESP-IDF export.sh: $IDF_EXPORT"
  echo "Hay chay lai voi IDF_EXPORT=/duong-dan/export.sh"
  exit 1
fi

source "$IDF_EXPORT"
cd "$PROJECT_DIR"
python3 scripts/release.py pocket-wall-e-c3 \
  --name pocket-wall-e-c3-pocket-esp-ai-by-huy-vector-en

echo
echo "Build xong. Firmware nam tai:"
echo "$PROJECT_DIR/build/merged-binary.bin"

