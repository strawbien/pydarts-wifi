#!/usr/bin/env python3
"""
test_wifi.py — Test du driver WiFi pyDarts sans lancer le jeu complet.

Usage :
  python test_wifi.py           → démarre le serveur WebSocket, attend l'ESP32
  python test_wifi.py --sim     → simule des frappes depuis le PC (sans ESP32)
  python test_wifi.py --port 9000  → port personnalisé (défaut : 8000)
"""

import asyncio
import json
import sys
import time
import queue
import threading

try:
    import websockets
except ImportError:
    print("[FATAL] websockets non installé. Lancez : pip install websockets")
    sys.exit(1)

PORT = 8000
for i, arg in enumerate(sys.argv):
    if arg == "--port" and i + 1 < len(sys.argv):
        PORT = int(sys.argv[i + 1])

SIM_MODE = "--sim" in sys.argv

# ─── Segments valides pour validation ────────────────────────────────────────
VALID_SEGMENTS = (
    [f"S{n}" for n in range(1, 21)] +
    [f"D{n}" for n in range(1, 21)] +
    [f"T{n}" for n in range(1, 21)] +
    ["SB", "DB", "PLAYERBUTTON", "GAMEBUTTON", "BACKUPBUTTON", "MISSDART"]
)

HIT_COUNT = 0

def validate(segment):
    if segment in VALID_SEGMENTS:
        return f"\033[92m✓ valide\033[0m"
    return f"\033[93m⚠ inconnu (vérifier le mapping)\033[0m"

# ─── Serveur WebSocket ────────────────────────────────────────────────────────
async def handler(websocket):
    global HIT_COUNT
    addr = websocket.remote_address
    print(f"\n\033[96m[CONNECT] ESP32 connecté depuis {addr}\033[0m")
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                segment = data.get("segment", "").upper()
                HIT_COUNT += 1
                status = validate(segment)
                print(f"  [{HIT_COUNT:>4}] {segment:<20} {status}  (raw: {message.strip()})")
            except (json.JSONDecodeError, AttributeError):
                print(f"  [WARN] Message invalide reçu : {message!r}")
    except websockets.exceptions.ConnectionClosed:
        print(f"\033[91m[DISCONNECT] ESP32 déconnecté ({addr})\033[0m")

async def run_server():
    print(f"\033[1m=== pyDarts WiFi Test Server ===\033[0m")
    print(f"  Écoute sur   : 0.0.0.0:{PORT}")
    print(f"  Chemin WS    : /ws")
    print(f"  Segments OK  : {len(VALID_SEGMENTS)}")
    print(f"  Ctrl+C pour arrêter\n")

    async with websockets.serve(handler, "0.0.0.0", PORT, process_request=check_path):
        await asyncio.Future()  # run forever

async def check_path(connection, request):
    """Accepte uniquement /ws, renvoie 404 sinon."""
    if request.path != "/ws":
        return connection.respond(404, "Not Found\n")

# ─── Mode simulation (sans ESP32) ────────────────────────────────────────────
SIM_HITS = [
    "T20", "S5", "D3", "SB", "DB",
    "T19", "D16", "S7",
    "PLAYERBUTTON", "GAMEBUTTON", "BACKUPBUTTON",
    "S1",  # segment inconnu ne peut pas exister ici mais test de validation
    "UNKNOWN_SEG",  # doit déclencher le warning ⚠
]

async def run_simulator():
    print(f"\033[1m=== pyDarts WiFi Simulator ===\033[0m")
    print(f"  Connexion à  : ws://127.0.0.1:{PORT}/ws")
    print(f"  Frappes      : {len(SIM_HITS)}\n")
    await asyncio.sleep(0.5)
    try:
        async with websockets.connect(f"ws://127.0.0.1:{PORT}/ws") as ws:
            print("\033[96m[CONNECT] Simulateur connecté\033[0m\n")
            for segment in SIM_HITS:
                payload = json.dumps({"segment": segment})
                await ws.send(payload)
                print(f"  → envoyé : {payload}")
                await asyncio.sleep(0.6)
            print("\n\033[92m[OK] Simulation terminée\033[0m")
    except ConnectionRefusedError:
        print("\033[91m[ERREUR] Serveur non joignable — lancez d'abord test_wifi.py dans un autre terminal\033[0m")
        sys.exit(1)

# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if SIM_MODE:
        asyncio.run(run_simulator())
    else:
        try:
            asyncio.run(run_server())
        except KeyboardInterrupt:
            print(f"\n\n[STOP] {HIT_COUNT} frappes reçues au total.")
