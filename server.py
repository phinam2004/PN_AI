import os
import sys
import json
import asyncio
import threading
import webbrowser
from typing import Set

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from core.platform_adapter import platform_adapter
from core.voice_engine import voice_engine
from core.ai_engine import ai_engine
from core.system_automation import system_automation
from core.command_registry import command_registry
from core.premium_features import premium_suite

app = FastAPI(title="Maya AI Cockpit Server")

# WebSocket client pool
active_connections: Set[WebSocket] = set()

# Server directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_HUD_DIR = os.path.join(BASE_DIR, "web_hud")

async def broadcast_ws(payload: dict):
    """Sends JSON message to all connected browsers."""
    dead_connections = set()
    for ws in list(active_connections):
        try:
            await ws.send_text(json.dumps(payload))
        except Exception:
            dead_connections.add(ws)
    for dead in dead_connections:
        active_connections.discard(dead)

def broadcast_ws_sync(payload: dict):
    """Synchronous bridge to broadcast WebSocket messages from worker threads."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.run_coroutine_threadsafe(broadcast_ws(payload), loop)
    except Exception:
        pass

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    print(f"[WebSocket] Client connected. Total clients: {len(active_connections)}")

    # Send initial welcome state
    init_telemetry = system_automation.get_telemetry()
    await websocket.send_text(json.dumps({
        "type": "telemetry",
        "data": init_telemetry
    }))

    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                msg = json.loads(raw_data)
            except Exception:
                msg = {"type": "command", "text": raw_data}

            msg_type = msg.get("type", "command")

            if msg_type == "command":
                user_text = msg.get("text", "").strip()
                if not user_text:
                    continue

                # 1. Update UI: Thinking state
                await broadcast_ws({
                    "type": "status",
                    "status": "THINKING",
                    "caption": f"PROCESSING: '{user_text}'"
                })

                # 2. Append user transcript
                await broadcast_ws({
                    "type": "transcript",
                    "sender": "User",
                    "text": user_text
                })

                # 3. Execute command on computer
                reply = command_registry.dispatch(user_text)

                # 4. Update UI: Speaking state
                await broadcast_ws({
                    "type": "status",
                    "status": "SPEAKING",
                    "caption": "MAYA IS EXECUTING..."
                })

                # 5. Append Maya transcript
                await broadcast_ws({
                    "type": "transcript",
                    "sender": "Maya",
                    "text": reply
                })

                # 6. Speak out loud through PC speakers
                voice_engine.speak(reply)

                # 7. Reset to Idle
                await asyncio.sleep(1.5)
                await broadcast_ws({
                    "type": "status",
                    "status": "IDLE",
                    "caption": "STANDBY // READY FOR WAKE WORD 'MAYA'"
                })

            elif msg_type == "persona":
                persona_key = msg.get("persona", "maya_default")
                res = premium_suite.switch_persona(persona_key)
                await broadcast_ws({
                    "type": "transcript",
                    "sender": "Maya",
                    "text": res
                })
                voice_engine.speak(res)

            elif msg_type == "workflow":
                workflow_name = msg.get("name", "")
                res = premium_suite.execute_workflow(workflow_name)
                await broadcast_ws({
                    "type": "transcript",
                    "sender": "Maya",
                    "text": res
                })
                voice_engine.speak(res)

    except WebSocketDisconnect:
        active_connections.discard(websocket)
        print("[WebSocket] Client disconnected.")
    except Exception as e:
        print(f"[WebSocket] Error: {e}")
        active_connections.discard(websocket)

@app.get("/api/telemetry")
def get_telemetry_api():
    return system_automation.get_telemetry()

@app.post("/api/command")
def execute_command_api(payload: dict):
    cmd = payload.get("command", "")
    reply = command_registry.dispatch(cmd)
    voice_engine.speak(reply)
    return {"command": cmd, "response": reply}

# Mount static web HUD files
app.mount("/", StaticFiles(directory=WEB_HUD_DIR, html=True), name="web_hud")

# Background telemetry broadcaster
async def telemetry_background_worker():
    while True:
        await asyncio.sleep(2.0)
        if active_connections:
            telemetry = system_automation.get_telemetry()
            await broadcast_ws({
                "type": "telemetry",
                "data": telemetry
            })

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(telemetry_background_worker())

# Background Native Microphone Listener (Voice Activation)
def native_mic_listener():
    """Continuously listens on PC microphone for 'Maya' wake word."""
    print("[Native Voice] Microphone listener thread initialized.")
    while True:
        try:
            detected_text = voice_engine.listen(timeout=3, phrase_time=4)
            if detected_text:
                lower_text = detected_text.lower()
                print(f"[Native Voice Heard]: {detected_text}")

                if "maya" in lower_text:
                    # Wake Word Detected!
                    broadcast_ws_sync({
                        "type": "status",
                        "status": "LISTENING",
                        "caption": "WAKE WORD DETECTED: 'MAYA' // LISTENING..."
                    })
                    voice_engine.speak("Yes boss?", sync=True)

                    # Listen for actual command
                    cmd = voice_engine.listen(timeout=6, phrase_time=7)
                    if cmd:
                        print(f"[Native Voice Command]: {cmd}")
                        broadcast_ws_sync({
                            "type": "transcript",
                            "sender": "User",
                            "text": cmd
                        })
                        broadcast_ws_sync({
                            "type": "status",
                            "status": "THINKING",
                            "caption": f"THINKING: '{cmd}'"
                        })

                        reply = command_registry.dispatch(cmd)

                        broadcast_ws_sync({
                            "type": "transcript",
                            "sender": "Maya",
                            "text": reply
                        })
                        broadcast_ws_sync({
                            "type": "status",
                            "status": "SPEAKING",
                            "caption": "MAYA RESPONDING..."
                        })
                        voice_engine.speak(reply)

                    broadcast_ws_sync({
                        "type": "status",
                        "status": "IDLE",
                        "caption": "STANDBY // READY FOR WAKE WORD 'MAYA'"
                    })
        except Exception as e:
            # Prevent loop crash
            pass

def start_server():
    """Starts FastAPI + Uvicorn server, pops open browser, and runs native mic listener."""
    # 1. Start native mic listener thread
    mic_thread = threading.Thread(target=native_mic_listener, daemon=True)
    mic_thread.start()

    # 2. Open browser at localhost:8000 after 1 second delay
    def open_browser():
        import time
        time.sleep(1.2)
        hud_url = "http://127.0.0.1:8000"
        try:
            if sys.platform == "win32":
                os.startfile(hud_url)
            else:
                webbrowser.open(hud_url)
        except Exception:
            webbrowser.open(hud_url)
        print(f"[OK] Maya Cockpit HUD launched at {hud_url}", flush=True)

    threading.Thread(target=open_browser, daemon=True).start()

    # 3. Speak welcoming message
    voice_engine.speak(f"Maya AI server is running on {platform_adapter.os_type}.")

    print("\n" + "="*60)
    print(" 🚀 MAYA AI FULL-STACK INTEGRATION SERVER")
    print(" 🌐 Web Cockpit HUD: http://127.0.0.1:8000")
    print(" 🎙️ Native PC Microphone: ACTIVE (Say 'Maya' to wake up)")
    print("="*60 + "\n")

    # 4. Run uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")

if __name__ == "__main__":
    start_server()
