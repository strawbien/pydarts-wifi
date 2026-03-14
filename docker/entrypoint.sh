#!/bin/bash
set -e

# ─── Variables ───────────────────────────────────────────────────────────────
DISPLAY_NUM=":99"
RESOLUTION="${PYDARTS_RESOLUTION:-1024x768x24}"
VNC_PORT="${VNC_PORT:-5900}"
NOVNC_PORT="${NOVNC_PORT:-6080}"
WIFI_PORT="${PYDARTS_WIFI_PORT:-8000}"

# ─── Config pyDarts ──────────────────────────────────────────────────────────
mkdir -p /root/.pydarts
cat > /root/.pydarts/pydarts.cfg << EOF
[SectionGlobals]
connection_type:wifi
wifi_port:${WIFI_PORT}
serialport:None
serialspeed:9600

[SectionAdvanced]
noserial:1

[SectionKeys]
S20:
S1:
S18:
S4:
S13:
S6:
S10:
S15:
S2:
S17:
S3:
S19:
S7:
S16:
S8:
S11:
S14:
S9:
S12:
S5:
D20:
D1:
D18:
D4:
D13:
D6:
D10:
D15:
D2:
D17:
D3:
D19:
D7:
D16:
D8:
D11:
D14:
D9:
D12:
D5:
T20:
T1:
T18:
T4:
T13:
T6:
T10:
T15:
T2:
T17:
T3:
T19:
T7:
T16:
T8:
T11:
T14:
T9:
T12:
T5:
SB:
DB:
PLAYERBUTTON:
GAMEBUTTON:
BACKUPBUTTON:
MISSDART:
EOF

echo "[BOOT] Config pyDarts créée (WiFi port ${WIFI_PORT})"

# ─── Affichage virtuel ───────────────────────────────────────────────────────
# ─── TigerVNC (X server + VNC en un seul processus) ─────────────────────────
echo "[BOOT] Démarrage TigerVNC ${DISPLAY_NUM} (${RESOLUTION}) sur port ${VNC_PORT}"
Xvnc ${DISPLAY_NUM} \
    -geometry ${RESOLUTION%x*} \
    -depth 24 \
    -rfbport ${VNC_PORT} \
    -SecurityTypes None \
    -localhost no \
    &
export DISPLAY=${DISPLAY_NUM}

# Attendre que le serveur VNC soit prêt
until [ -e /tmp/.X${DISPLAY_NUM#:}-lock ] 2>/dev/null || \
      nc -z localhost ${VNC_PORT} 2>/dev/null; do
    sleep 0.3
done
sleep 0.5
echo "[BOOT] TigerVNC prêt"

# ─── noVNC ───────────────────────────────────────────────────────────────────
echo "[BOOT] Démarrage noVNC sur port ${NOVNC_PORT}"
websockify --web /usr/share/novnc ${NOVNC_PORT} localhost:${VNC_PORT} &
sleep 1

echo "[BOOT] Interface disponible sur http://[IP_NAS]:${NOVNC_PORT}/vnc.html"

# ─── Variables SDL ───────────────────────────────────────────────────────────
export SDL_VIDEODRIVER=x11
export SDL_AUDIODRIVER=dummy    # évite les crashs audio dans le container

# ─── pyDarts ─────────────────────────────────────────────────────────────────
echo "[BOOT] Lancement de pyDarts"
cd /app/pydarts
exec python pydarts.py
