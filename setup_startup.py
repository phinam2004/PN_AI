import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def get_startup_dir() -> str:
    appdata = os.environ.get("APPDATA", "")
    return os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs", "Startup")

def install_startup():
    startup_dir = get_startup_dir()
    os.makedirs(startup_dir, exist_ok=True)
    vbs_path = os.path.join(startup_dir, "PhiNamAI.vbs")

    project_dir = os.path.abspath(os.path.dirname(__file__))
    assistant_path = os.path.join(project_dir, "phi_nam_assistant.py")

    vbs_content = (
        'Set WshShell = CreateObject("WScript.Shell")\n'
        f'WshShell.CurrentDirectory = "{project_dir}"\n'
        f'WshShell.Run "pythonw.exe """ & "{assistant_path}" & """", 0, False\n'
    )

    with open(vbs_path, "w", encoding="utf-8") as f:
        f.write(vbs_content)

    if os.path.exists(vbs_path):
        print(f"[THÀNH CÔNG] Đã cài đặt Phi Nam AI tự khởi động cùng Windows!")
        print(f"[VỊ TRÍ]: {vbs_path}")
        return True
    return False

def uninstall_startup():
    startup_dir = get_startup_dir()
    vbs_path = os.path.join(startup_dir, "PhiNamAI.vbs")
    if os.path.exists(vbs_path):
        os.remove(vbs_path)
        print("[THÀNH CÔNG] Đã gỡ bỏ Phi Nam AI khỏi thư mục khởi động Windows.")
        return True
    else:
        print("[THÔNG BÁO] Chưa cài đặt khởi động cùng Windows.")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "uninstall":
        uninstall_startup()
    else:
        install_startup()
