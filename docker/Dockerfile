FROM python:3.11.9-slim

ENV DEBIAN_FRONTEND=noninteractive

# ─── Système ────────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y \
    # Affichage virtuel + VNC (tout-en-un, plus fiable que Xvfb+x11vnc)
    tigervnc-standalone-server \
    # noVNC + websockify
    novnc websockify \
    # SDL / pygame
    libsdl2-2.0-0 libsdl2-image-2.0-0 libsdl2-mixer-2.0-0 libsdl2-ttf-2.0-0 \
    # Audio virtuel (évite les crashs pygame)
    libasound2 \
    # espeak pour pyttsx3
    espeak \
    # Utilitaires
    curl netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# ─── Dépendances Python ──────────────────────────────────────────────────────
RUN pip install pygame pyserial websockets netifaces2 pyttsx3 requests pexpect zeroconf

# ─── Code source ─────────────────────────────────────────────────────────────
WORKDIR /app
COPY pydarts/ ./pydarts/

# ─── Entrypoint ──────────────────────────────────────────────────────────────
COPY docker/index.html /usr/share/novnc/index.html
COPY docker/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh && chmod +x /entrypoint.sh

# ─── Ports ───────────────────────────────────────────────────────────────────
# 6080 → noVNC (navigateur)
# 8000 → WebSocket pyDarts (ESP32)
EXPOSE 6080 8000

ENTRYPOINT ["/entrypoint.sh"]
