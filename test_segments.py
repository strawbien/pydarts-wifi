#!/usr/bin/env python3
"""
test_segments.py — Vérification complète du mapping de la matrice ESP32.

Usage :
  python test_segments.py            → port 8000
  python test_segments.py --port 9000

Frappe chaque zone de la cible. Le tableau se met à jour en temps réel.
Appuie sur Ctrl+C pour voir le rapport final.
"""

import asyncio
import json
import sys
import os

try:
    import websockets
except ImportError:
    print("[FATAL] pip install websockets")
    sys.exit(1)

PORT = 8000
for i, arg in enumerate(sys.argv):
    if arg == "--port" and i + 1 < len(sys.argv):
        PORT = int(sys.argv[i + 1])

# ─── Liste complète des segments attendus ────────────────────────────────────
SINGLES  = [f"S{n}" for n in [20,1,18,4,13,6,10,15,2,17,3,19,7,16,8,11,14,9,12,5]]
DOUBLES  = [f"D{n}" for n in [20,1,18,4,13,6,10,15,2,17,3,19,7,16,8,11,14,9,12,5]]
TRIPLES  = [f"T{n}" for n in [20,1,18,4,13,6,10,15,2,17,3,19,7,16,8,11,14,9,12,5]]
BULLS    = ["SB", "DB"]
BUTTONS  = ["PLAYERBUTTON", "GAMEBUTTON", "BACKUPBUTTON", "MISSDART"]

ALL_SEGMENTS = SINGLES + DOUBLES + TRIPLES + BULLS + BUTTONS
TOTAL = len(ALL_SEGMENTS)

# État : None = pas testé, True = OK, False = inconnu
state = {s: None for s in ALL_SEGMENTS}
hit_count = 0
unknown_hits = []

# ─── Affichage ───────────────────────────────────────────────────────────────
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def cell(seg):
    s = state[seg]
    if s is None:
        return f"\033[90m{seg:<14}\033[0m"   # gris = pas encore testé
    return f"\033[92m{seg:<14}\033[0m"        # vert = reçu

def print_board():
    clear()
    tested = sum(1 for v in state.values() if v is not None)
    print(f"\033[1m=== Test Segments pyDarts WiFi ===\033[0m  "
          f"{tested}/{TOTAL} testés  |  {hit_count} frappes reçues\n")

    print("\033[1mSingles\033[0m")
    print("  " + "  ".join(cell(s) for s in SINGLES[:10]))
    print("  " + "  ".join(cell(s) for s in SINGLES[10:]))

    print("\n\033[1mDoubles\033[0m")
    print("  " + "  ".join(cell(s) for s in DOUBLES[:10]))
    print("  " + "  ".join(cell(s) for s in DOUBLES[10:]))

    print("\n\033[1mTriples\033[0m")
    print("  " + "  ".join(cell(s) for s in TRIPLES[:10]))
    print("  " + "  ".join(cell(s) for s in TRIPLES[10:]))

    print("\n\033[1mBulls\033[0m")
    print("  " + "  ".join(cell(s) for s in BULLS))

    print("\n\033[1mBoutons\033[0m")
    print("  " + "  ".join(cell(s) for s in BUTTONS))

    if unknown_hits:
        print(f"\n\033[93m⚠ Segments inconnus reçus : {', '.join(set(unknown_hits))}\033[0m")

    # Segments pas encore testés
    missing = [s for s, v in state.items() if v is None]
    if missing:
        print(f"\n\033[90mManquants ({len(missing)}) : {', '.join(missing)}\033[0m")
    else:
        print(f"\n\033[92m✓ Tous les segments ont été testés !\033[0m")

    print("\n  Ctrl+C pour rapport final")

# ─── Serveur WebSocket ────────────────────────────────────────────────────────
async def handler(websocket):
    global hit_count
    print_board()
    async for message in websocket:
        try:
            data = json.loads(message)
            segment = data.get("segment", "").upper()
            hit_count += 1
            if segment in state:
                state[segment] = True
            else:
                unknown_hits.append(segment)
            print_board()
        except (json.JSONDecodeError, AttributeError):
            pass

async def run():
    print(f"En attente de l'ESP32 sur le port {PORT}...\n")
    async with websockets.serve(handler, "0.0.0.0", PORT,
                                process_request=check_path):
        await asyncio.Future()

async def check_path(connection, request):
    if request.path != "/ws":
        return connection.respond(404, "Not Found\n")

# ─── Rapport final ────────────────────────────────────────────────────────────
def print_report():
    tested  = [s for s, v in state.items() if v is not None]
    missing = [s for s, v in state.items() if v is None]
    print(f"\n\033[1m=== Rapport final ===\033[0m")
    print(f"  Testés   : {len(tested)}/{TOTAL}")
    if missing:
        print(f"\n  \033[91mNon testés ({len(missing)}) :\033[0m")
        for s in missing:
            print(f"    - {s}")
    else:
        print(f"\n  \033[92m✓ Mapping complet validé !\033[0m")
    if unknown_hits:
        print(f"\n  \033[93m⚠ Segments inconnus reçus :\033[0m")
        for s in set(unknown_hits):
            print(f"    - {s}")

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print_report()
