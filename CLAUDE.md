# pyDarts WiFi Fork — Contexte du projet

## Objectif

Fork de [pyDarts](https://sourceforge.net/projects/pydarts/) (GPLv3) pour ajouter une couche de communication **WiFi/WebSocket** en complément du driver série USB existant.

L'idée est de permettre à un **ESP32** de se connecter sans fil à pyDarts, sans modifier le comportement existant pour les utilisateurs Arduino/USB.

---

## Architecture hardware

```
Cible électronique (soft tip)
    └── Matrice FFC (2 nappes : 10 pins + 7 pins)
        └── ESP32 DevKit V1 30 pins (WiFi natif)
            └── WiFi
                └── pyDarts (Python) sur PC/Synology NAS
                    └── Écran / Tablette (navigateur)
```

## Matériel

- **Cible** : cible électronique soft tip reconditionnée (PCB d'origine retiré)
- **Microcontrôleur** : ESP32 DevKit V1 30 pins
- **Connexion matrice** : nappes FFC soudées vers pins GPIO ESP32
- **Serveur** : Synology NAS avec Docker, ou PC Linux

---

## Mapping de la matrice (7×10 = 70 intersections)

### Pins GPIO utilisés

| Rôle | GPIO |
|---|---|
| Masters (nappe 10 pins) | 2, 4, 5, 13, 14, 15, 18, 19, 21, 22 |
| Slaves (nappe 7 pins) | 12, 23, 25, 26, 27, 32, 33 |

### Table de mapping complète

| Segment | Master | Slave |
|---|---|---|
| 20 | 15 | 25 |
| 1 | 18 | 25 |
| 18 | 19 | 25 |
| 4 | 21 | 25 |
| 13 | 22 | 25 |
| 6 | 22 | 32 |
| 10 | 21 | 32 |
| 15 | 19 | 32 |
| 2 | 18 | 32 |
| 17 | 15 | 32 |
| 3 | 4 | 32 |
| 19 | 5 | 32 |
| 7 | 13 | 32 |
| 16 | 14 | 32 |
| 8 | 15 | 12 |
| 11 | 21 | 12 |
| 14 | 14 | 25 |
| 9 | 13 | 25 |
| 12 | 5 | 25 |
| 5 | 4 | 25 |
| D20 | 15 | 23 |
| D1 | 18 | 23 |
| D18 | 19 | 23 |
| D4 | 21 | 23 |
| D13 | 22 | 23 |
| D6 | 22 | 27 |
| D10 | 21 | 27 |
| D15 | 19 | 27 |
| D2 | 18 | 27 |
| D17 | 15 | 27 |
| D3 | 4 | 27 |
| D19 | 5 | 27 |
| D7 | 13 | 27 |
| D16 | 14 | 27 |
| D8 | 18 | 12 |
| D11 | 22 | 12 |
| D14 | 14 | 23 |
| D9 | 13 | 23 |
| D12 | 5 | 23 |
| D5 | 4 | 23 |
| T20 | 15 | 26 |
| T1 | 18 | 26 |
| T18 | 19 | 26 |
| T4 | 21 | 26 |
| T13 | 22 | 26 |
| T6 | 22 | 33 |
| T10 | 21 | 33 |
| T15 | 19 | 33 |
| T2 | 18 | 33 |
| T17 | 15 | 33 |
| T3 | 4 | 33 |
| T19 | 5 | 33 |
| T7 | 13 | 33 |
| T16 | 14 | 33 |
| T8 | 4 | 12 |
| T11 | 19 | 12 |
| T14 | 14 | 26 |
| T9 | 13 | 26 |
| T12 | 5 | 26 |
| T5 | 4 | 26 |
| 25 (bull outer) | 13 | 12 |
| 50 (bull) | 5 | 12 |
| BTN_PLAYER | 2 | 4 |
| BTN_DOUB | 2 | 15 |
| BTN_RESET | 2 | 18 |
| BTN_HOLD | 2 | 19 |
| BTN_GAMES | 2 | 21 |
| BTN_OPTIONS | 2 | 22 |

---

## Code ESP32 existant

### Structure des fichiers

```
pydarts-wifi/
├── CLAUDE.md           ← ce fichier
├── esp32/
│   ├── dartboard_test_v2.ino   ← version test avec serveur web
│   ├── dartboard_esp32.ino     ← version finale avec WebSocket
│   └── config.h                ← paramètres WiFi et serveur
└── (code pyDarts original)
```

### config.h

```cpp
const char* WIFI_SSID     = "TON_SSID";
const char* WIFI_PASSWORD = "TON_MOT_DE_PASSE";
const char* WS_HOST       = "192.168.1.45";  // IP du serveur pyDarts
const int   WS_PORT       = 8000;
const char* WS_PATH       = "/ws";
```

### Format des messages WebSocket envoyés par l'ESP32

```json
{"segment": "T20"}
{"segment": "D5"}
{"segment": "25"}
{"segment": "BTN_PLAYER"}
```

---

## Travail à faire dans pyDarts

### Objectif

Ajouter un driver WiFi/WebSocket **optionnel** sans casser le driver série existant.

### Architecture cible

```
pyDarts
├── drivers/
│   ├── serial_driver.py     ← existant, non modifié
│   └── wifi_driver.py       ← à créer (WebSocket server)
└── config.py                ← ajouter: connection_type = serial | wifi
                                         wifi_port = 8000
```

### Protocole à implémenter

Le driver WiFi doit :
1. Ouvrir un serveur WebSocket sur le port configuré
2. Recevoir les messages JSON de l'ESP32 : `{"segment": "T20"}`
3. Traduire le segment en événement pyDarts (même format que le driver série)
4. Gérer la reconnexion automatique si l'ESP32 se déconnecte

### Analyse du driver série existant à faire

Avant de coder le driver WiFi, il faut comprendre :
- Le format exact des données envoyées par l'Arduino via série
- Comment pyDarts interprète ces données
- Où injecter le nouveau driver dans l'architecture Python

---

## Décisions prises

- Fork public prévu une fois la fonctionnalité validée
- Licence : GPLv3 (comme pyDarts original)
- Les auteurs originaux (Diego, Poilou) ont été contactés sur SourceForge
- L'ESP32 envoie les segments en JSON via WebSocket
- Le mapping matrice est complet et validé physiquement
- Anti-rebond de 500ms implémenté côté ESP32

---

## Références

- [pyDarts original](https://sourceforge.net/projects/pydarts/)
- [Wiki pyDarts](https://pydarts.lovecoop.fr)
- [Règles des jeux](https://pydarts.lovecoop.fr/doku.php?id=pydarts_games_rules)
- [Documentation Arduino sketch pyDarts](https://pydarts.lovecoop.fr/doku.php?id=arduino_sketch_file_for_pydarts)
