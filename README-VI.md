# KALEZ AI cho ESP32-C3 SuperMini

KALEZ AI là firmware tùy biến dựa trên nền tảng XiaoZhi và source Pocket ESP AI
của Huy Vector. Bản build nhắm tới ESP32-C3 SuperMini 4 MB, OLED SSD1306
128x64, microphone INMP441 và amplifier MAX98357A.

Source nền tảng và ghi nhận tác giả được giữ trong `source/xiaozhi-esp32`; xem
`source/xiaozhi-esp32/LICENSE` và các thông tin bản quyền đi kèm.

## Phần cứng

| Linh kiện | Chân ESP32-C3 |
| --- | ---: |
| OLED SDA / SCL | GPIO21 / GPIO20 |
| INMP441 SCK / WS / SD | GPIO2 / GPIO1 / GPIO8 |
| MAX98357A BCLK / LRC / DIN | GPIO2 / GPIO1 / GPIO3 |
| Nút chức năng | GPIO10 |

BCLK và WS/LRC được dùng chung cho microphone và amplifier. Nối INMP441 L/R
xuống GND; cấp 3.3 V cho OLED và microphone, 5 V cho amplifier, và nối chung GND.
Không thay đổi GPIO trong board profile nếu phần cứng đang hàn theo sơ đồ này.

## Wi-Fi và XiaoZhi Cloud

Firmware dùng cơ chế Wi-Fi provisioning sẵn có của XiaoZhi. Nếu chưa lưu Wi-Fi,
thiết bị vào chế độ cấu hình; sau khi kết nối Wi-Fi, firmware tiếp tục kiểm tra
OTA/activation và nạp cấu hình MQTT hoặc WebSocket từ dịch vụ.

Tên **KALEZ AI** hiển thị trên OLED và được dùng làm DHCP hostname. Board name,
Device ID, Client ID, endpoint và User-Agent gửi tới Cloud vẫn theo cấu hình
XiaoZhi hiện có để tránh làm sai định danh mà server yêu cầu.

## Build bằng GitHub Actions

Workflow `.github/workflows/build-esp32c3.yml` dùng ESP-IDF 5.5.2 và profile
`pocket-wall-e-c3` cho target `esp32c3`, flash 4 MB và partition
`partitions/v2/4m.csv`. Từ repository trên GitHub, mở **Actions**, chọn
**Build ESP32-C3 SuperMini firmware**, rồi chọn **Run workflow**. Artifact chỉ
có sau khi job build và đóng gói hoàn tất thành công.

Artifact chứa:

- `merged-binary.bin` để nạp nguyên image tại offset `0x0`.
- Các BIN thành phần và offset do ESP-IDF tạo trong `flasher_args.json`.
- `partition-table.bin`, `4m-partitions.csv`, manifest TXT/JSON và SHA-256.

Nạp merged image bằng esptool theo lệnh được ghi trong `FLASH-MANIFEST.txt`.
Lệnh trong manifest lấy flash mode, flash size và tần số từ metadata build; thay
`COMx` bằng cổng thiết bị. Merged image được ghi tại `0x0`. Nếu nạp các BIN
riêng, dùng đúng offset trong manifest; không trộn merged image với các BIN
riêng trong cùng lệnh.

## Build cục bộ

Máy build cần ESP-IDF 5.5.2 cùng ESP-IDF Component Manager. Từ thư mục
`source/xiaozhi-esp32`, chạy:

```sh
python scripts/release.py pocket-wall-e-c3 --name pocket-wall-e-c3-pocket-esp-ai-by-huy-vector-en
```

Lệnh này build đúng profile, tạo `build/merged-binary.bin` và gói build trong
`releases/`. Chạy thêm script đóng gói để tạo manifest giống CI:

```sh
python scripts/package_firmware_artifacts.py
```

## Firmware binary có sẵn trong gói nguồn

`firmware/pocket-esp-ai-by-huy-vector-english.bin` là binary gốc do Huy Vector
cung cấp, không phải bản KALEZ AI được build từ những thay đổi hiện tại. SHA-256
được cung cấp cùng gói gốc: `3d9dc6d68cc0eebaacb05f20fb4cc49fda7802eda21400483f1d9fcf2a01cf98`.

Chưa có build GitHub Actions hoặc build ESP-IDF cục bộ trong môi trường này;
chưa thể cung cấp binary KALEZ AI mới hay xác nhận hoạt động trên phần cứng thật.
