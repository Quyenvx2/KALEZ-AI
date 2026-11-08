# Pocket ESP AI by Huy Vector

Project XiaoZhi AI dành cho ESP32-C3 SuperMini, màn OLED SSD1306 0.96 inch,
micro INMP441 và ampli MAX98357A.

## Nội dung gói

- `firmware/pocket-esp-ai-by-huy-vector-english.bin`: firmware hoàn chỉnh,
  nạp tại địa chỉ `0x0`.
- `source/xiaozhi-esp32`: toàn bộ mã nguồn có thể build lại.
- `FLASH-FIRMWARE.command`: nạp nhanh firmware trên macOS.
- `BUILD-FIRMWARE.command`: build lại source bằng ESP-IDF.

## Tính năng hiện tại

- Giao diện tiếng Anh.
- Wake word: **Hi ESP**.
- Tên thiết bị: **pocket-esp-ai-by-huy-vector**.
- Mắt hoạt hình toàn bộ vùng trên của OLED, dòng trạng thái ở phía dưới.
- Màn OLED đảo màu theo cấu hình hiện tại.
- Thu âm bằng INMP441, phát âm thanh qua MAX98357A.
- Có xử lý DC và AGC cho tín hiệu micro.
- Wi-Fi provisioning của XiaoZhi và nút chức năng ngoài.

## Sơ đồ đấu dây

| Thiết bị | Chân module | ESP32-C3 SuperMini |
| --- | --- | ---: |
| OLED SSD1306 | SDA | GPIO21 |
| OLED SSD1306 | SCL | GPIO20 |
| INMP441 | SCK/BCLK | GPIO2 |
| INMP441 | WS/LRC | GPIO1 |
| INMP441 | SD | GPIO8 |
| INMP441 | L/R | GND |
| MAX98357A | BCLK | GPIO2 |
| MAX98357A | LRC | GPIO1 |
| MAX98357A | DIN | GPIO3 |
| Nút chức năng | một đầu | GPIO10 |
| Nút chức năng | đầu còn lại | GND |

Nguồn:

- OLED và INMP441: `3.3V`.
- MAX98357A: `5V`.
- Tất cả module phải nối chung `GND`.
- BCLK và LRC được dùng chung giữa micro và ampli.

## Nạp nhanh trên macOS

1. Cắm ESP32-C3 bằng cáp USB có truyền dữ liệu.
2. Mở file `FLASH-FIRMWARE.command`.
3. Nếu macOS chặn file, vào **System Settings > Privacy & Security** và chọn
   **Open Anyway**, hoặc chạy trong Terminal:

```sh
chmod +x FLASH-FIRMWARE.command
./FLASH-FIRMWARE.command
```

Script tự tìm cổng `/dev/cu.usb*`. Có thể chỉ định cổng thủ công:

```sh
PORT=/dev/cu.usbmodemXXXX ./FLASH-FIRMWARE.command
```

## Build lại source

Máy cần cài ESP-IDF. Bản này đã được build bằng ESP-IDF 5.5.2. Chạy:

```sh
IDF_EXPORT=/duong-dan/toi/esp-idf/export.sh ./BUILD-FIRMWARE.command
```

Nếu không truyền `IDF_EXPORT`, script sẽ thử đường dẫn đã dùng trên máy phát
triển:

`/Users/huyvector/esp/v5.5.2/esp-idf/export.sh`

Sau khi build thành công, firmware một-file nằm tại:

`source/xiaozhi-esp32/build/merged-binary.bin`

## Build bằng GitHub Actions

Workflow `.github/workflows/build-esp32c3.yml` build biến thể ESP32-C3 bằng
ESP-IDF 5.5.2, sau đó đăng artifact để tải trong mục **Actions** của GitHub.
Có thể chạy thủ công bằng **Run workflow** hoặc để workflow tự chạy khi có thay
đổi source.

Artifact chứa `merged-binary.bin` (nạp tại offset `0x0`), các BIN thành phần,
`4m-partitions.csv`, bảng phân vùng nhị phân và `FLASH-MANIFEST.txt` / JSON.
Offset của từng BIN thành phần được trích từ metadata do chính ESP-IDF tạo trong
lần build đó; không điền offset giả định vào workflow. Script đóng gói cũng kiểm
tra ảnh ứng dụng vừa factory partition trước khi xuất artifact.

Ví dụ nạp merged BIN bằng esptool:

```sh
python -m esptool --chip esp32c3 --port COMx --baud 460800 write_flash 0x0 merged-binary.bin
```

Thay `COMx` bằng cổng nối với bo mạch. Để nạp các BIN thành phần riêng, dùng
đúng danh sách offset trong `FLASH-MANIFEST.txt`. Không dùng `merged-binary.bin`
cùng lúc với các BIN thành phần trong cùng lệnh.

## Lưu ý

- Firmware hiện tại được thiết kế để dùng đủ OLED, micro và ampli. OLED sai địa
  chỉ hoặc đấu sai có thể khiến thiết bị khởi động lại trước khi phát Wi-Fi.
- GPIO8 trên một số board C3 SuperMini còn nối với LED tích hợp. Nếu micro bị
  nhiễu, cần kiểm tra phiên bản board thực tế.
- Build thành công không thay thế cho việc thử trực tiếp toàn bộ phần cứng.

SHA-256 của firmware:

`3d9dc6d68cc0eebaacb05f20fb4cc49fda7802eda21400483f1d9fcf2a01cf98`

