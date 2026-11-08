#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="${0:A:h}"
FIRMWARE="$SCRIPT_DIR/firmware/pocket-esp-ai-by-huy-vector-english.bin"
IDF_EXPORT="${IDF_EXPORT:-/Users/huyvector/esp/v5.5.2/esp-idf/export.sh}"

if [[ ! -f "$FIRMWARE" ]]; then
  echo "Khong tim thay firmware: $FIRMWARE"
  exit 1
fi

if [[ -f "$IDF_EXPORT" ]]; then
  source "$IDF_EXPORT"
fi

if [[ -z "${PORT:-}" ]]; then
  PORT=$(find /dev -maxdepth 1 \( -name 'cu.usbmodem*' -o -name 'cu.usbserial*' \) -print -quit)
fi

if [[ -z "${PORT:-}" ]]; then
  echo "Khong tim thay cong USB. Hay cam lai board va thu:"
  echo "PORT=/dev/cu.usbmodemXXXX ./FLASH-FIRMWARE.command"
  exit 1
fi

echo "Dang nap qua cong: $PORT"
python3 -m esptool --chip esp32c3 -p "$PORT" -b 460800 \
  --before default_reset --after hard_reset \
  write_flash 0x0 "$FIRMWARE"

echo
echo "Nap thanh cong. ESP32-C3 dang khoi dong lai."

