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

# Mẫu nhận diện từ khóa đánh thức toàn diện ở đầu câu:
# Xử lý trọn vẹn cả các biến thể âm học Google Speech API thường nghe thành: "Việt Nam", "Vina mới", "Vinamilk", "Phi Lam", "Khi Nam"...
WAKE_PREFIX_PATTERN = re.compile(
    r'^(?:alo\s+|hey\s+|chào\s+|ê\s+|em\s+)?'
    r'(?:phi\s*nam|việt\s*nam|vinamilk|vina\s*mới|vina|phi\s*lam|phi\s*lan|vi\s*nam|khi\s*nam|kỳ\s*nam|thì\s*nam|huy\s*nam|maya|trợ\s*lý)'
    r'(?:\s+ơi|\s+oi|\s+à|\s+nè|\s+đâu)?'
    r'(?:\s+hãy|\s+em|\s+làm\s+ơn|\s+giúp\s+anh|\s+giúp\s+tôi)?\s*',
    re.IGNORECASE
)

def detect_wake_and_extract_command(text: str):
    """
    Kiểm tra xem câu nói có chứa từ khóa gọi tên Phi Nam không.
    Tách từ khóa sạch sẽ ở đầu câu để lấy câu lệnh phía sau.
    """
    if not text:
        return False, ""

    clean = text.strip()
    match = WAKE_PREFIX_PATTERN.match(clean)
    if match:
        cmd = clean[match.end():].strip()
        cmd = re.sub(r'^(ơi|em|hãy|làm ơn|giúp anh|giúp tôi|nhé)\s*', '', cmd, flags=re.IGNORECASE).strip()
        return True, cmd

    return False, clean

def run_phi_nam_assistant():
    print("\n" + "="*65, flush=True)
    print(" 🤖 TRỢ LÝ ẢO PHI NAM AI (PHIÊN BẢN CHẠY TRỰC TIẾP TRÊN MÁY TÍNH)", flush=True)
    print(" 🎙️ TỪ KHÓA KÍCH HOẠT: 'Phi Nam' hoặc 'Phi Nam ơi'", flush=True)
    print(" 💡 KHÔNG CẦN MỞ WEB - Đang lắng nghe trực tiếp từ Micro...", flush=True)
    print(" ❌ Nhấn Ctrl + C hoặc nói 'Tạm biệt Phi Nam' để tắt", flush=True)
    print("="*65 + "\n", flush=True)

    # Cân chỉnh độ nhạy micro theo môi trường phòng (chống điếc mic)
    voice_engine.calibrate_microphone()

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

            # Trường hợp 1: Có từ khóa gọi tên VÀ có câu lệnh đi kèm (VD: "Phi Nam ơi mở nhạc Thánh Ca trên YouTube")
            if has_wake and inline_cmd and len(inline_cmd) >= 2:
                print(f"\n>>> ĐÃ KÍCH HOẠT & THỰC THI LỆNH: {inline_cmd} <<<", flush=True)
                voice_engine.play_wake_chime()
                reply = command_registry.dispatch(inline_cmd)
                if reply == "TERMINATE_SESSION":
                    if not voice_engine.play_cached_audio("goodbye.wav", sync=True):
                        voice_engine.speak("Dạ, tạm biệt anh Phi Nam. Chúc anh một ngày tốt lành!", sync=True)
                    break
                if reply:
                    print(f"[Phi Nam phản hồi]: {reply}", flush=True)
                    voice_engine.speak(reply, sync=True)

            # Trường hợp 2: Chỉ gọi tên "Phi Nam ơi" (chưa có câu lệnh đi kèm)
            elif has_wake and not inline_cmd:
                print("\n>>> ĐÃ KÍCH HOẠT TRỢ LÝ PHI NAM! <<<", flush=True)
                voice_engine.play_wake_chime()
                if not voice_engine.play_cached_audio("wake_response.wav", sync=True):
                    voice_engine.speak("Dạ, em nghe anh Phi Nam!", sync=True)

                print("[Đang lắng nghe câu lệnh tiếp theo của anh...] ", flush=True)
                cmd = voice_engine.listen(timeout=6, phrase_time=7)

                if cmd:
                    print(f"[Câu lệnh nhận được]: {cmd}", flush=True)
                    cmd_is_wake, clean_subcmd = detect_wake_and_extract_command(cmd)
                    target_cmd = clean_subcmd if clean_subcmd else cmd
                    if not target_cmd or len(target_cmd) < 2:
                        voice_engine.speak("Dạ em đây ạ! Anh muốn em mở ứng dụng gì hay làm gì ạ?", sync=True)
                    else:
                        reply = command_registry.dispatch(target_cmd)
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

            # Trường hợp 3: Người dùng nói thẳng câu lệnh hành động mà không gọi tên (VD: "Mở nhạc Thánh Ca trên YouTube ngay lập tức")
            elif command_registry.can_handle(voice_text):
                print(f"\n[Nhận diện lệnh hành động trực tiếp]: {voice_text}", flush=True)
                voice_engine.play_wake_chime()
                reply = command_registry.dispatch(voice_text)
                if reply == "TERMINATE_SESSION":
                    if not voice_engine.play_cached_audio("goodbye.wav", sync=True):
                        voice_engine.speak("Dạ, tạm biệt anh Phi Nam. Chúc anh một ngày tốt lành!", sync=True)
                    break
                if reply:
                    print(f"[Thực thi nhanh]: {reply}", flush=True)
                    voice_engine.speak(reply, sync=True)

        except KeyboardInterrupt:
            print("\nĐã dừng trợ lý Phi Nam AI.", flush=True)
            break
        except Exception as e:
            time.sleep(0.5)

    voice_engine.shutdown()

if __name__ == "__main__":
    run_phi_nam_assistant()
