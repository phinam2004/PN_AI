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
| `README.md` | Cập nhật | Tài liệu kỹ thuật hoàn chỉnh cho phiên bản v1.2 |

---

## 2. Chi Tiết Kỹ Thuật Đã Triển Khai

1. **Khử hoàn toàn lỗi nền tảng độc quyền của macOS:**
   - Thay thế lệnh gọi `os.system('say ...')` bằng `VoiceEngine` hỗ trợ `edge-tts` và SAPI5 / PowerShell trên Windows.
   - Thay thế `subprocess.run(["mdfind", ...])` bằng `platform_adapter.find_and_open_folder(...)` quét thông minh các thư mục Windows, macOS, Linux.
   - Thay thế `open -a` bằng logic phân giải registry và PATH cross-platform.
2. **Loại bỏ hiện tượng đơ luồng (Non-blocking):**
   - Hàng đợi TTS chạy ngầm trong luồng worker riêng biệt.
   - Loại bỏ độ trễ `adjust_for_ambient_noise(0.5)` lặp đi lặp lại.
3. **Giao diện thế hệ mới:**
   - Tạo mới giao diện Cockpit HUD trực quan sống động phản hồi trạng thái: `IDLE`, `LISTENING`, `THINKING`, `SPEAKING`.
4. **Trí tuệ nhân tạo có trí nhớ:**
   - `ai_engine.py` lưu trữ 10 lượt hội thoại gần nhất, hỗ trợ Persona linh hoạt và fallback thông minh không bị sập khi chưa có Ollama.

👉 **Tự động chuyển giao sang Chặng 3 (QA Tester & Kiểm Thử).**
