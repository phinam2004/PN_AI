"""
=============================================================================
PHI NAM AI - TRỢ LÝ ẢO ĐIỀU KHIỂN BẰNG GIỌNG NÓI TRÊN MÁY TÍNH
- Kích hoạt bằng giọng nói: "Phi Nam", "Phi Nam ơi", "Hey Phi Nam"
- Chạy trực tiếp trên Windows, KHÔNG CẦN MỞ TRÌNH DUYỆT WEB
- Tự động hóa hệ thống: Mở app, tăng giảm âm lượng, chụp màn hình, tìm kiếm...
=============================================================================
"""

import os
import sys
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from core.platform_adapter import platform_adapter
from core.voice_engine import voice_engine
from core.command_registry import command_registry
from core.system_automation import system_automation

# Danh sách từ khóa đánh thức trợ lý
WAKE_WORDS = [
    "phi nam",
    "phinam",
    "phi nam ơi",
    "phi nam oi",
    "hey phi nam",
    "ê phi nam",
    "e phi nam",
    "chào phi nam",
    "maya" # Giữ lại làm từ khóa phụ
]

def is_wake_word(text: str) -> bool:
    """Kiểm tra xem câu nói có chứa từ khóa gọi tên Phi Nam không."""
    if not text:
        return False
    clean = text.lower().strip()
    return any(w in clean for w in WAKE_WORDS)

def run_phi_nam_assistant():
    print("\n" + "="*65)
    print(" 🤖 TRỢ LÝ ẢO PHI NAM AI (PHIÊN BẢN CHẠY TRỰC TIẾP TRÊN MÁY TÍNH)")
    print(" 🎙️ TỪ KHÓA KÍCH HOẠT: 'Phi Nam' hoặc 'Phi Nam ơi'")
    print(" 💡 KHÔNG CẦN MỞ WEB - Đang lắng nghe trực tiếp từ Micro...")
    print(" ❌ Nhấn Ctrl + C hoặc nói 'Tạm biệt Phi Nam' để tắt")
    print("="*65 + "\n")

    # Phát âm thanh khởi động
    voice_engine.play_wake_chime()
    voice_engine.speak("Trợ lý ảo Phi Nam đã sẵn sàng phục vụ anh.", sync=True)

    is_running = True

    while is_running:
        try:
            # 1. Lắng nghe từ khóa đánh thức
            print("[Đang nghe từ khóa 'Phi Nam']...", end="\r", flush=True)
            voice_text = voice_engine.listen(timeout=3, phrase_time=4)

            if not voice_text:
                time.sleep(0.3)
                continue

            print(f"\n[Âm thanh nhận dạng]: {voice_text}")

            if is_wake_word(voice_text):
                # Đã gọi đúng tên Phi Nam!
                print("\n>>> ĐÃ KÍCH HOẠT TRỢ LÝ PHI NAM! <<<")
                voice_engine.play_wake_chime()
                voice_engine.speak("Dạ, em nghe anh Phi Nam!", sync=True)

                # 2. Tiếp nhận câu lệnh tiếp theo
                print("[Đang nghe câu lệnh của anh...] ")
                cmd = voice_engine.listen(timeout=6, phrase_time=8)

                if cmd:
                    print(f"[Câu lệnh nhận được]: {cmd}")
                    reply = command_registry.dispatch(cmd)

                    if reply == "TERMINATE_SESSION":
                        voice_engine.speak("Dạ, tạm biệt anh Phi Nam. Chúc anh một ngày làm việc hiệu quả!", sync=True)
                        is_running = False
                        break

                    if reply:
                        print(f"[Phi Nam phản hồi]: {reply}")
                        voice_engine.speak(reply, sync=True)
                else:
                    voice_engine.speak("Em chưa nghe rõ lệnh, anh cần em giúp gì cứ gọi Phi Nam nhé!", sync=True)

            else:
                # Kiểm tra nếu người dùng nói thẳng lệnh (ví dụ: 'tăng âm lượng', 'chụp màn hình')
                # Nếu câu lệnh khớp với hệ thống, vẫn hỗ trợ thực thi nhanh
                lower_text = voice_text.lower()
                if any(k in lower_text for k in ["tăng âm lượng", "giảm âm lượng", "chụp màn hình", "tắt tiếng", "mở chrome", "mở vs code"]):
                    reply = command_registry.dispatch(voice_text)
                    if reply and reply != "TERMINATE_SESSION":
                        print(f"[Thực thi nhanh]: {reply}")
                        voice_engine.speak(reply, sync=True)

        except KeyboardInterrupt:
            print("\nĐã dừng trợ lý Phi Nam AI.")
            break
        except Exception as e:
            # Ngăn ngừa sập vòng lặp
            time.sleep(0.5)

    voice_engine.shutdown()

if __name__ == "__main__":
    run_phi_nam_assistant()
