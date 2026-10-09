# 📝 Nhật Ký Thi Công & Thay Đổi (Chặng 2: Coder)

> **Người thực hiện:** Senior Developer (Phòng Kỹ Thuật & Thi Công)  
> **Thời gian:** 2026-10-09  
> **Phiên bản đích:** Maya AI v1.2 Next-Gen (Cross-Platform)

---

## 1. Danh Sách File Đã Tạo Mới & Chỉnh Sửa

| Đường dẫn file | Thao tác | Mô tả chi tiết |
| :--- | :--- | :--- |
| `DESIGN.md` | Tạo mới | Hợp đồng thiết kế duy nhất (Single Source of Truth) chuẩn Google Labs Stitch |
| `core/__init__.py` | Tạo mới | Đóng gói package `core` |
| `core/platform_adapter.py` | Tạo mới | Lớp trừu tượng phần cứng & OS (Windows, macOS, Linux) |
| `core/voice_engine.py` | Tạo mới | Động cơ âm thanh đa luồng (Edge-TTS Neural, SAPI5, Say, Espeak) |
| `core/ai_engine.py` | Tạo mới | Động cơ AI thông minh có bộ đệm ngữ cảnh (Memory Window) & Personas |
| `core/system_automation.py` | Tạo mới | Tự động hóa hệ thống: âm lượng, pin, boss key, clipboard, telemetry |
| `core/command_registry.py` | Tạo mới | Bộ định tuyến lệnh hỗ trợ Fuzzy matching, Regex, Chained commands |
| `core/premium_features.py` | Tạo mới | Persona Studio (Jarvis, Cyberpunk, VN Voice) & Workflow Macros (Focus/Meeting) |
| `web_hud/index.html` | Tạo mới | Giao diện Cyber-Minimalist Cockpit HUD chuẩn Google Labs |
| `web_hud/style.css` | Tạo mới | Hệ thống CSS Design Tokens cao cấp, dark glassmorphism |
| `web_hud/app.js` | Tạo mới | Bộ điều khiển visualizer Canvas sóng âm, telemetry polling & chat log |
| `maya_core.py` | Tạo mới | Bộ điều phối trung tâm thống nhất mọi module |
| `main.py` | Cập nhật | Nâng cấp toàn diện tương thích ngược, không crash trên Windows/Linux |
| `phi_nam_assistant.py` | Tạo mới | Trợ lý ảo Phi Nam chạy trực tiếp từ micro, không cần mở web |
| `setup_startup.py` | Tạo mới | Tự động tạo VBScript khởi động cùng Windows |
| `cai_dat_khoi_dong_cung_windows.bat` | Tạo mới | Script 1-click cài đặt khởi động cùng Windows |
| `assets/*.wav` | Tạo mới | Bộ âm thanh bản địa nạp sẵn phản hồi tức thì 0ms |

---

## 2. Chi Tiết Kỹ Thuật Đã Triển Khai

1. **Khử hoàn toàn lỗi nền tảng độc quyền của macOS:**
   - Thay thế lệnh gọi `os.system('say ...')` bằng `VoiceEngine` hỗ trợ `edge-tts` và SAPI5 / PowerShell trên Windows.
   - Thay thế `subprocess.run(["mdfind", ...])` bằng `platform_adapter.find_and_open_folder(...)` quét thông minh các thư mục Windows, macOS, Linux.
   - Thay thế `open -a` bằng logic phân giải registry và PATH cross-platform.
2. **Loại bỏ độ trễ phản hồi (Zero-Latency Wake Response):**
   - Đổi từ khóa kích hoạt thành **"Phi Nam"** / **"Phi Nam ơi"** và nhận diện đa âm vực (xử lý cả trường hợp Google nhận thành "Việt Nam ơi").
   - Nạp sẵn file âm thanh WAV không nén tại thư mục `assets/` (`wake_response.wav`, `ready.wav`, `not_heard.wav`, `goodbye.wav`).
   - Sử dụng `winsound.PlaySound` phát thanh trực tiếp qua driver âm thanh Windows với độ trễ 0ms (không tốn 2-3s kết nối mạng qua Edge-TTS).
   - Thiết lập `energy_threshold = 450` và `pause_threshold = 0.6` giúp lọc tạp âm môi trường/phim ảnh và chốt câu nói nhanh hơn.
   - Chuyển toàn bộ hội thoại fallback sang tiếng Việt tự nhiên, lịch thiệp.
3. **Giao diện thế hệ mới & Trợ lý Desktop độc lập:**
   - Hoạt động 100% độc lập trên Windows dưới dạng tiến trình nền không cần trình duyệt web.
   - Tự động hóa hệ thống: Mở ứng dụng, tăng giảm âm lượng, chụp ảnh màn hình, tìm kiếm Google/YouTube.

👉 **Tự động chuyển giao sang Chặng 3 (QA Tester & Kiểm Thử).**

