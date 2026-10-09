"""
=============================================================================
PHI NAM AI - TRỢ LÝ ẢO ĐIỀU KHIỂN BẰNG GIỌNG NÓI TRÊN MÁY TÍNH
- Kích hoạt bằng giọng nói: "Phi Nam", "Phi Nam ơi", "Hey Phi Nam"
- Nhận diện nhạy bén (bắt trọn cả các trường hợp Google nghe thành 'Việt Nam ơi')
- Chạy trực tiếp trên Windows, KHÔNG CẦN MỞ TRÌNH DUYỆT WEB
- Tự động hóa hệ thống: Mở app, tăng giảm âm lượng, chụp màn hình, tìm kiếm...
=============================================================================
"""

import os
import sys
import time
import re

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

from core.platform_adapter import platform_adapter
from core.voice_engine import voice_engine
from core.command_registry import command_registry
from core.system_automation import system_automation

# Danh sách từ khóa đánh thức trợ lý (Bao gồm cả các biến thể âm học Google Speech API dễ nghe)
WAKE_WORDS = [
    "phi nam ơi",
    "phi nam oi",
    "phi nam",
    "phinam",
    "hey phi nam",
    "ê phi nam",
    "e phi nam",
    "chào phi nam",
    # Các biến thể do Google Speech API tự sửa chính tả:
    "việt nam ơi",
    "việt nam oi",
    "viet nam oi",
    "việt nam",
    "viet nam",
    "khi nam",
    "thì nam",
    "huy nam",
    "vi nam",
    "maya"
]

def detect_wake_and_extract_command(text: str):
    """
    Kiểm tra xem câu nói có chứa từ khóa gọi tên Phi Nam không.
    Nếu có lệnh đi kèm trong cùng 1 câu (ví dụ: 'Phi Nam ơi mở Chrome'),
    tách riêng câu lệnh để thực thi ngay lập tức.
    """
    if not text:
        return False, ""

    clean = text.lower().strip()
    matched_wake = None
    for w in WAKE_WORDS:
        if w in clean:
            matched_wake = w
            break

    if not matched_wake:
        return False, ""

    # Loại bỏ từ khóa đánh thức để lấy phần câu lệnh đi kèm (nếu có)
    remainder = clean.replace(matched_wake, "").strip()
    # Loại bỏ các từ đệm ở đầu như: "ơi", "ơi em", "hãy", "làm ơn", "giúp anh"
    remainder = re.sub(r'^(ơi|em|hãy|làm ơn|giúp anh|giúp tôi|nhé)\s*', '', remainder).strip()

    return True, remainder

def run_phi_nam_assistant():
    print("\n" + "="*65, flush=True)
    print(" 🤖 TRỢ LÝ ẢO PHI NAM AI (PHIÊN BẢN CHẠY TRỰC TIẾP TRÊN MÁY TÍNH)", flush=True)
    print(" 🎙️ TỪ KHÓA KÍCH HOẠT: 'Phi Nam' hoặc 'Phi Nam ơi'", flush=True)
    print(" 💡 KHÔNG CẦN MỞ WEB - Đang lắng nghe trực tiếp từ Micro...", flush=True)
    print(" ❌ Nhấn Ctrl + C hoặc nói 'Tạm biệt Phi Nam' để tắt", flush=True)
    print("="*65 + "\n", flush=True)

    # Phát âm thanh chuông và câu chào khởi động siêu tốc 0ms
    voice_engine.play_wake_chime()
    if not voice_engine.play_cached_audio("ready.wav", sync=True):
        voice_engine.speak("Trợ lý ảo Phi Nam đã sẵn sàng phục vụ anh.", sync=True)

    is_running = True

    while is_running:
        try:
            print("[Đang nghe từ khóa 'Phi Nam']...", end="\r", flush=True)
            voice_text = voice_engine.listen(timeout=4, phrase_time=5)

            if not voice_text:
                time.sleep(0.2)
                continue

            print(f"\n[Âm thanh nhận dạng]: {voice_text}", flush=True)

            has_wake, inline_cmd = detect_wake_and_extract_command(voice_text)

            if has_wake:
                print("\n>>> ĐÃ KÍCH HOẠT TRỢ LÝ PHI NAM! <<<", flush=True)
                voice_engine.play_wake_chime()

                # Trường hợp 1: Người dùng nói gộp cả tên và lệnh (VD: "Phi Nam ơi mở Chrome")
                if inline_cmd and len(inline_cmd) >= 3:
                    print(f"[Thực thi lệnh đi kèm]: {inline_cmd}", flush=True)
                    reply = command_registry.dispatch(inline_cmd)
                    if reply == "TERMINATE_SESSION":
                        if not voice_engine.play_cached_audio("goodbye.wav", sync=True):
                            voice_engine.speak("Dạ, tạm biệt anh Phi Nam. Chúc anh một ngày tốt lành!", sync=True)
                        break
                    if reply:
                        print(f"[Phi Nam phản hồi]: {reply}", flush=True)
                        voice_engine.speak(reply, sync=True)

                # Trường hợp 2: Người dùng chỉ gọi tên "Phi Nam ơi"
                else:
                    # Phản hồi tức thì 0ms bằng file âm thanh bản địa đã nạp sẵn
                    if not voice_engine.play_cached_audio("wake_response.wav", sync=True):
                        voice_engine.speak("Dạ, em nghe anh Phi Nam!", sync=True)

                    print("[Đang lắng nghe câu lệnh tiếp theo của anh...] ", flush=True)
                    cmd = voice_engine.listen(timeout=5, phrase_time=6)

                    if cmd:
                        print(f"[Câu lệnh nhận được]: {cmd}", flush=True)
                        cmd_is_wake, extracted = detect_wake_and_extract_command(cmd)
                        if cmd_is_wake and (not extracted or len(extracted) < 3):
                            voice_engine.speak("Dạ em đây ạ! Anh muốn em mở ứng dụng gì hay làm gì ạ?", sync=True)
                        else:
                            final_cmd = extracted if (cmd_is_wake and extracted) else cmd
                            reply = command_registry.dispatch(final_cmd)

                            if reply == "TERMINATE_SESSION":
                                if not voice_engine.play_cached_audio("goodbye.wav", sync=True):
                                    voice_engine.speak("Dạ, tạm biệt anh Phi Nam. Chúc anh một ngày tốt lành!", sync=True)
                                break

                            if reply:
                                print(f"[Phi Nam phản hồi]: {reply}", flush=True)
                                voice_engine.speak(reply, sync=True)
                    else:
                        if not voice_engine.play_cached_audio("not_heard.wav", sync=True):
                            voice_engine.speak("Dạ, em chưa nghe rõ. Anh cần em giúp gì cứ gọi Phi Nam nhé!", sync=True)

            else:
                # Nếu người dùng nói thẳng lệnh phổ biến mà quên gọi tên
                lower_text = voice_text.lower()
                direct_cmds = [
                    "mở chrome", "bật chrome", "mở vs code", "mở code",
                    "tăng âm lượng", "giảm âm lượng", "tắt tiếng", "bật tiếng",
                    "chụp màn hình", "khóa màn hình", "ẩn hết cửa sổ"
                ]
                if any(k in lower_text for k in direct_cmds):
                    reply = command_registry.dispatch(voice_text)
                    if reply and reply != "TERMINATE_SESSION":
                        print(f"[Thực thi nhanh]: {reply}", flush=True)
                        voice_engine.play_wake_chime()
                        voice_engine.speak(reply, sync=True)

        except KeyboardInterrupt:
            print("\nĐã dừng trợ lý Phi Nam AI.", flush=True)
            break
        except Exception as e:
            time.sleep(0.5)

    voice_engine.shutdown()

if __name__ == "__main__":
    run_phi_nam_assistant()
