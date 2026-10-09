# 📐 Bản Vẽ Kiến Trúc & Kế Hoạch Nâng Cấp Maya AI (v1.2 -> v1.7 / v2.0)
**Chặng 1: Ban Kế Hoạch & Kiến Trúc (Planner / CEO)**  
**Dự án:** Maya AI Cross-Platform Voice Assistant Engine  
**Mục tiêu:** Kiểm tra, phân tích chi tiết toàn diện và thiết kế lộ trình kỹ thuật để nâng cấp 10 tính năng cốt lõi cho Maya AI.

---

## 1. Hiện Trạng Kỹ Thuật (Audit Codebase Hiện Tại)

Hiện tại, codebase gồm 4 file chính:
1. `main.py` (281 dòng):
   - **Tập trung hoàn toàn vào macOS**:
     - `os.system('say "..."')` chỉ chạy trên macOS. Chạy trên Windows/Linux sẽ báo lỗi command not found.
     - `subprocess.run(["mdfind", foldername])`: `mdfind` là Spotlight Search độc quyền của macOS.
     - `subprocess.run(["open", "-a", "..."])`: Lệnh `open -a` mở app của macOS, vô hiệu trên Windows và Linux.
     - `os.system(f"open {file_path}")` cho screenshot: lỗi trên Windows/Linux.
   - **Xử lý đồng bộ (Blocking Architecture)**:
     - Hàm `speak()` chạy đồng bộ chặn luồng chính.
     - `listen_command()` chặn luồng tối đa 8 giây mỗi vòng lặp.
     - Mỗi vòng lặp đều gọi `recognizer.adjust_for_ambient_noise(source, duration=0.5)` gây trễ cứng 500ms lãng phí.
     - Lời gọi `ask_local_ai()` qua Ollama chờ phản hồi toàn phần từ mô hình, không stream token.
   - **Giao diện thô sơ**:
     - Hàm `show_startup_gif()` tạo file `maya_animation.html` mở trên trình duyệt mặc định, chỉ hiển thị ảnh GIF tĩnh/lặp, không có sự liên kết, tương tác hai chiều (two-way binding) với tiến trình AI.
     - `gif_viewer.py` dùng Tkinter nhưng bị bỏ rơi, không được tích hợp vào `main.py`.
   - **Nhận diện giọng nói**:
     - Hardcode ngôn ngữ `en-IN` (Indian English), không thể đổi sang tiếng Anh Mỹ `en-US` hay tiếng Việt `vi-VN`.
     - Phụ thuộc 100% vào Google Speech API trực tuyến, mất mạng là tê liệt.
   - **Xử lý lệnh giọng nói**:
     - Chuỗi `if/elif` sơ sài với hàm `in` hoặc `startswith()`, không chịu được biến thể câu từ, không có fuzzy matching hoặc slot extraction.

---

## 2. Phân Tích Chi Tiết 10 Tính Năng Yêu Cầu

### 2.1 🌍 Windows Support
- **Vấn đề cần giải:** Thay thế các cơ chế macOS độc quyền bằng API Windows tương thích chuẩn.
- **Giải pháp kỹ thuật:**
  - **TTS Engine:** Hỗ trợ `edge-tts` (Microsoft Edge Neural Voices - cực mượt và tự nhiên) kết hợp fallback Windows SAPI5 (`pyttsx3` / `winsound` / `sounddevice`).
  - **Khởi chạy ứng dụng:** Dùng `os.startfile(app_target)` hoặc truy xuất PowerShell `Get-StartApps`, Windows Registry (`App Paths`), hoặc đường dẫn `AppData/Local/Programs/`.
  - **Tìm kiếm thư mục:** Dùng `os.walk` có giới hạn độ sâu hoặc lệnh `where`, `powershell Get-ChildItem -Directory -Filter`, tìm kiếm các thư mục chuẩn của Windows (`%USERPROFILE%/Downloads`, `Desktop`, `Documents`).
  - **Screenshot:** Mở file ảnh chụp bằng `os.startfile(file_path)` trên Windows.

### 2.2 🍎 macOS Support
- **Vấn đề cần giải:** Chuẩn hóa lại các tính năng macOS hiện có vào một lớp trừu tượng (Abstraction Layer), không để hardcode rời rạc.
- **Giải pháp kỹ thuật:**
  - Giữ lại hỗ trợ cho lệnh `say` của macOS hoặc nâng cấp lên Neural TTS của Edge.
  - Tối ưu lệnh `mdfind` với bộ lọc loại trừ file hệ thống rác, sắp xếp theo độ khớp và thời gian truy cập gần nhất.
  - Xử lý mượt các ứng dụng bundle `.app` qua `open -a` và AppleScript.
  - Bổ sung kiểm tra quyền Micro (`AVCaptureDevice`) và Accessibility (`AXIsProcessTrusted`).

### 2.3 🐧 Linux Support
- **Vấn đề cần giải:** Tương thích các bản phân phối Ubuntu, Debian, Fedora, Arch.
- **Giải pháp kỹ thuật:**
  - **TTS:** Hỗ trợ `spd-say`, `espeak-ng` hoặc `edge-tts`.
  - **Mở ứng dụng/file:** Sử dụng `xdg-open`.
  - **Tìm kiếm:** Dùng `locate` / `find` hoặc quét thư mục `~/.local/share/applications` để lấy danh sách `.desktop`.
  - **Audio/Mic:** Tương thích PulseAudio / PipeWire / ALSA.

### 2.4 🧠 Smarter AI Engine
- **Vấn đề cần giải:** AI hiện tại chỉ là hàm gọi `ollama.chat(model="llama3")` 1 lượt, không có trí nhớ, không có Persona, sập ngay nếu chưa bật Ollama.
- **Giải pháp kỹ thuật:**
  - **Kiến trúc Hybrid Multi-Tier:**
    - *Tier 1 (Instant Slot Extractor):* Phân loại ý định (Intent) tức thì bằng Regex + Keyword scoring. Lệnh hệ thống chạy ngay trong < 10ms.
    - *Tier 2 (Local LLM with Context):* Hỗ trợ Ollama (Llama 3, Phi-3, Qwen 2.5, Mistral) với Sliding Window Conversation History (lưu trữ 10 lượt hội thoại gần nhất).
    - *Tier 3 (Cloud Fallback):* Tích hợp fallback sang OpenAI / Gemini / Groq API khi Ollama không bật hoặc máy yếu.
  - **System Persona:** Cài đặt Prompt cốt lõi định hình Maya thành trợ lý ảo thông minh, dí dỏm, ngắn gọn, phản hồi chuẩn xác cho trợ lý giọng nói (dưới 2 câu khi đàm thoại thông thường).

### 2.5 ⚡ Faster Performance
- **Vấn đề cần giải:** Khắc phục tình trạng đơ, giật lag, chờ đợi nhận diện.
- **Giải pháp kỹ thuật:**
  - Chuyển sang mô hình **Event-Driven Non-blocking Loop**:
    - Luồng 1 (Ear Thread): Lắng nghe âm thanh liên tục, chỉ hiệu chỉnh `adjust_for_ambient_noise` 1 lần lúc khởi động và duy trì ngưỡng năng lượng động (`dynamic_energy_threshold = True`).
    - Luồng 2 (Brain Thread): Xử lý AI và logic lệnh qua hàng đợi `queue.Queue`.
    - Luồng 3 (Voice Thread): Phát âm thanh phản hồi bất đồng bộ, có thể ngắt lời (Barge-in capability) khi người dùng nói từ khóa can thiệp.
  - Stream TTS: Chia câu trả lời của AI thành từng câu ngắn (dấu chấm, dấu phẩy) để vừa sinh câu đầu đã phát âm thanh ngay, giảm độ trễ Time-to-First-Audio (TTFA) xuống dưới 400ms.

### 2.6 🎨 Modern User Interface
- **Vấn đề cần giải:** Chấm dứt việc bật tab web tĩnh vô tri chứa ảnh GIF.
- **Giải pháp kỹ thuật:**
  - Xây dựng giao diện **Real-time Glassmorphism Cockpit HUD** tuân thủ 100% `DESIGN.md` (Google Labs standard):
    - Chạy backend local server nhẹ (FastAPI/WebSocket hoặc HTTP bridge tích hợp).
    - **Visualizer sóng âm sống động:** Canvas/SVG phản ứng với âm lượng micro (Visual Amplitude).
    - **Trạng thái trực quan:** `IDLE` (Xanh Cyan lững lờ), `LISTENING` (Sóng dập dìu), `THINKING` (Vòng xoay hổ phách), `SPEAKING` (Sóng phổ âm tần).
    - **Transcript Stream:** Hiển thị thời gian thực nội dung người nói và câu trả lời của Maya.
    - **System Telemetry Bar:** Giám sát CPU, RAM, Pin, Tình trạng mạng, Model AI đang kích hoạt.

### 2.7 🎙️ Improved Voice Recognition
- **Vấn đề cần giải:** Nghe sai, phụ thuộc mạng, nhận diện kém khi có tiếng ồn.
- **Giải pháp kỹ thuật:**
  - Hỗ trợ đa ngôn ngữ: Cấu hình linh hoạt giữa tiếng Anh (`en-US`), tiếng Việt (`vi-VN`), hoặc tự nhận diện.
  - Tích hợp động cơ nhận dạng offline: Mô hình Vosk siêu nhẹ hoặc Whisper Base/Tiny (chạy hoàn toàn offline, độ trễ cực thấp, bảo mật tối đa).
  - Tự động lọc tạp âm: Lọc tần số cao/thấp cơ bản trước khi đẩy qua bộ nhận diện.

### 2.8 🤖 Advanced AI Automation
- **Vấn đề cần giải:** Thiếu khả năng kiểm soát phần cứng và ứng dụng thực tế.
- **Giải pháp kỹ thuật:**
  - Điều khiển đa phương tiện: Tăng/giảm/tắt âm lượng (`volume`), Play/Pause nhạc.
  - Điều khiển hiển thị: Chỉnh độ sáng màn hình, khóa máy (`Lock Workstation`), chế độ Sleep.
  - Quản lý ứng dụng: Tự động đóng tác vụ nặng, dọn dẹp RAM, thu nhỏ tất cả cửa sổ (Boss Key: `Win + D` / `Cmd + F3`).
  - Tương tác Clipboard: Đọc nội dung đang copy, tóm tắt bài báo vừa copy, dịch đoạn văn bản vừa copy.
  - Quản lý pin: Cảnh báo khi pin dưới 20% hoặc khi sạc đầy 80%.

### 2.9 🔥 More Powerful Voice Commands
- **Vấn đề cần giải:** Câu lệnh cứng nhắc, sai một chữ là không nhận.
- **Giải pháp kỹ thuật:**
  - **Hệ thống Plugin Registry mở rộng:** Kiến trúc `@command(name, keywords, category, handler)`.
  - **Fuzzy Keyword Matching:** Dùng thuật toán Levenshtein distance hoặc tỷ lệ tương đồng `difflib.SequenceMatcher` để hiểu được câu khi người dùng phát âm chưa chuẩn (VD: "lauch vs code", "o-pen chrom").
  - **Lệnh phức hợp (Chained Commands):** Tách câu bằng các liên từ "và", "and", "then" để thực thi liên tiếp nhiều tác vụ (VD: "Chụp màn hình rồi mở thư mục downloads").
  - **LLM Function Calling Fallback:** Khi câu lệnh không khớp với bất kỳ từ khóa nào, đẩy vào LLM để sinh JSON định dạng lệnh thực thi.

### 2.10 💎 Exclusive Premium Features
- **Vấn đề cần giải:** Tạo giá trị vượt trội so với trợ lý miễn phí thông thường.
- **Giải pháp kỹ thuật:**
  - **Persona Studio (Đổi nhân cách):**
    - `Jarvis`: Tác phong chuẩn mực, trung thành, công nghệ cao.
    - `Cyberpunk Hacker`: Ngắn gọn, lạnh lùng, dùng thuật ngữ mã nguồn.
    - `Executive Secretary`: Lịch thiệp, tập trung vào hiệu suất, tóm tắt nhanh.
  - **Edge-TTS Ultra-Natural Voices:** Tùy chọn giọng đọc AI chuẩn Studio (Microsoft Neural Voices) với âm sắc ấm áp, giàu cảm xúc, không bị cảm giác máy móc như `say` cũ.
  - **Workflow Macro 1-Click:** Thiết lập các profile tự động hóa:
    - *"Focus Mode":* Mở VS Code + Bật nhạc lofi + Tắt thông báo + Đặt âm lượng 35%.
    - *"Meeting Mode":* Tắt micro hệ thống + Bật chế độ ghi chép + Mở Google Meet.
  - **Privacy Shield Mode (100% Offline):** Tắt toàn bộ kết nối cloud, chỉ sử dụng Vosk STT + Llama 3 Offline + Local TTS.

---

## 3. Kiến Trúc Module & Danh Sách File Cần Triển Khai

```
c:\Users\PC\Documents\GitHub\PN_AI\
├── core/
│   ├── __init__.py
│   ├── platform_adapter.py    # Abstraction cho Windows, macOS, Linux
│   ├── ai_engine.py           # Hybrid AI (Local Ollama, Cloud, Memory buffer)
│   ├── voice_engine.py        # Quản lý mic, STT, TTS (Edge-TTS / SAPI / macOS)
│   ├── system_automation.py   # Điều khiển âm lượng, pin, app, clipboard
│   ├── command_registry.py    # Decorator-based router, fuzzy matching, compound actions
│   └── premium_features.py    # Persona Studio, Workflows, Telemetry diagnostics
├── web_hud/
│   ├── index.html             # Google Labs compliant Futuristic HUD
│   ├── style.css              # Dark Glassmorphism CSS Tokens
│   └── app.js                 # WebSocket visualizer, telemetry feeds, audio anim
├── DESIGN.md                  # Hợp đồng thiết kế duy nhất (Đã khởi tạo)
├── maya_core.py               # Engine điều phối chính (Event loop & Service runner)
├── main.py                    # Điểm khởi chạy chính đa nền tảng
└── requirements.txt           # Danh mục dependencies tối ưu
```

---

## 4. Kế Hoạch Kiểm Thử (QA & Test Strategy)
- Kiểm tra nhập khẩu (Import test) và tính tương thích trên Windows (hệ thống hiện tại).
- Kiểm tra tính chịu lỗi (Fault tolerance): chạy mượt mà ngay cả khi không có mic hoặc không có Ollama (Graceful degradation).
- Kiểm tra tính tuân thủ thiết kế `DESIGN.md`.
- Kiểm tra benchmark tốc độ phản hồi của Command Router (< 5ms).

👉 **Chuyển giao Chặng 2 (Phòng Kỹ Thuật & Coder):** Tiến hành tạo các module và hoàn thiện mã nguồn giải pháp theo đúng bản vẽ kiến trúc.
