# pyDarts WiFi

A fork of [pyDarts v1.2.0](https://sourceforge.net/projects/pydarts/files/pydarts/1.2.0/) (2022-08-23) that adds a **WiFi/WebSocket driver**, allowing an ESP32 to replace the original Arduino USB connection.

> Original pyDarts by [@Poilou](https://sourceforge.net/u/poilou/profile/) and [@Diego](https://sourceforge.net/u/diego2/profile/) — licensed under GPLv3.

---

## What this fork adds

- **`pydarts/include/wifi_driver.py`** — WebSocket server that receives dart hits from the ESP32
- **`dartboard_esp32/dartboard_esp32.ino`** — ESP32 firmware that scans the dart matrix and sends hits over WiFi
- **`connection_type:wifi`** config option — drop-in replacement for the serial driver, no changes to game logic

The serial driver is untouched. Both modes coexist.

---

## Hardware

```
Soft-tip dart board (reconditioned, original PCB removed)
    └── FFC ribbon cables (10-pin + 7-pin)
        └── ESP32 DevKit V1 (30 pins)
            └── WiFi
                └── pyDarts (PC or NAS)
```

### Matrix pins

| Role | GPIO pins |
|------|-----------|
| Masters (10-pin ribbon, outputs) | 2, 4, 5, 13, 14, 15, 18, 19, 21, 22 |
| Slaves (7-pin ribbon, inputs + pull-up) | 12, 23, 25, 26, 27, 32, 33 |

70 intersections mapped (singles, doubles, triples, bulls, 6 buttons).

---

## Requirements

### Python (server side)
```bash
pip install pygame pyserial websockets netifaces2 pyttsx3 requests
```
Python 3.9–3.11 recommended.

### Arduino (ESP32 firmware)
Install via Arduino Library Manager:
- **WebSockets** by Markus Sattler
- **ArduinoJson** by Benoit Blanchon

Board: `ESP32 Dev Module`

---

## Setup

### 1. ESP32 firmware

```bash
cp dartboard_esp32/config.h.example dartboard_esp32/config.h
```

Edit `config.h` with your WiFi credentials and the IP of your pyDarts server:

```cpp
const char* WIFI_SSID     = "your-ssid";
const char* WIFI_PASSWORD = "your-password";
const char* WS_HOST       = "192.168.1.x";  // IP of the machine running pyDarts
const int   WS_PORT       = 8000;
const char* WS_PATH       = "/ws";
```

Flash `dartboard_esp32/dartboard_esp32.ino` to your ESP32.

### 2. pyDarts config

Create `~/.pydarts/pydarts.cfg`:

```ini
[SectionGlobals]
connection_type:wifi
wifi_port:8000

[SectionAdvanced]
noserial:1

[SectionKeys]
S20:
S1:
# ... (leave values empty, WiFi mode does not use char mapping)
```

### 3. Run

```bash
cd pydarts
python pydarts.py
```

---

## Testing

Test the WebSocket layer without launching pyDarts:

```bash
# Terminal 1 — start the test server
python test_wifi.py

# Terminal 2 — simulate ESP32 hits from the PC
python test_wifi.py --sim
```

Test all 68 matrix segments with a live checklist:

```bash
python test_segments.py
```

---

## Docker deployment

Run pyDarts in a container with a browser-accessible interface (no local display required).

### Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop) with Compose

### Quick start

```bash
docker compose -f docker/docker-compose.yml up --build
```

Open `http://localhost:6080` in your browser — pyDarts loads automatically.

### Ports

| Port | Usage |
|------|-------|
| `6080` | noVNC web interface (pyDarts UI in the browser) |
| `8000` | WebSocket server (ESP32 connection) |

### Synology NAS

```bash
git clone https://github.com/Supatoshi/pydarts-wifi.git
cd pydarts-wifi
docker compose -f docker/docker-compose.yml up -d
```

Access via `http://<NAS_IP>:6080`.

Point your ESP32 `config.h` to `WS_HOST = "<NAS_IP>"`.

### Scores persistence

Game scores are stored in a Docker volume (`pydarts-scores`) and survive container restarts.

### Development workflow

Use local Docker for development, NAS for production:

```bash
# local dev — rebuilds on each change
docker compose -f docker/docker-compose.yml up --build

# NAS — pull latest and redeploy
git pull && docker compose -f docker/docker-compose.yml up -d --build
```

---

## Project structure

```
pydarts-wifi/
├── pydarts/                  # pyDarts source (original + WiFi additions)
│   ├── pydarts.py
│   └── include/
│       ├── CInput.py         # modified: Wifi_Connect / Wifi_Read
│       ├── CConfig.py        # modified: connection_type, wifi_port options
│       └── wifi_driver.py    # new: WebSocket server
├── dartboard_esp32/          # ESP32 firmware
│   ├── dartboard_esp32.ino
│   ├── config.h              # your credentials (gitignored)
│   └── config.h.example
├── arduino/                  # original Arduino sketches (unmodified)
├── docker/                   # Docker deployment
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── entrypoint.sh
│   └── index.html            # noVNC auto-connect page
├── test_wifi.py              # WebSocket server + simulator
├── test_segments.py          # full matrix test checklist
└── LICENSE                   # GPLv3
```

---

## How it works

The ESP32 scans the 10×7 dart matrix and sends a JSON message on each hit:

```json
{"segment": "T20"}
```

pyDarts runs a WebSocket server (`wifi_driver.py`) that receives these messages and feeds them directly into the input loop — the same path as the serial driver. No changes to game logic.

Segment names match pyDarts' internal score map (`T20` → 60 pts, `SB` → 25 pts, etc.).

---

## Credits

- **pyDarts** — [@Poilou](https://sourceforge.net/u/poilou/profile/) & [@Diego](https://sourceforge.net/u/diego2/profile/) ([sourceforge](https://sourceforge.net/projects/pydarts/), [wiki](https://pydarts.lovecoop.fr))
- **WiFi fork** — [@Supatoshi](https://github.com/Supatoshi)

---

## License

GPLv3 — see [LICENSE](LICENSE).
