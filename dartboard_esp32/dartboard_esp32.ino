/*
 * dartboard_esp32.ino
 * ESP32 WebSocket client for pyDarts WiFi driver
 *
 * Scans the dart matrix (10 masters x 7 slaves) and sends hits
 * to the pyDarts WebSocket server as JSON: {"segment":"T20"}
 *
 * Library required: WebSocketsClient (Markus Sattler / arduinoWebSockets)
 * Install via Arduino Library Manager: "WebSockets by Markus Sattler"
 */

#include <WiFi.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>
#include "config.h"

// ─── Matrix pins ────────────────────────────────────────────────────────────
const int NUM_MASTERS = 10;
const int NUM_SLAVES  = 7;

// Masters → outputs (driven LOW one at a time)
const int masterPins[NUM_MASTERS] = {2, 4, 5, 13, 14, 15, 18, 19, 21, 22};

// Slaves → inputs with pull-up (read LOW when hit)
const int slavePins[NUM_SLAVES]   = {12, 23, 25, 26, 27, 32, 33};

// ─── Segment mapping ─────────────────────────────────────────────────────────
struct SegmentMap {
  int         master;
  int         slave;
  const char* segment;   // pyDarts key name (matches SectionKeys in pydarts.cfg)
};

const SegmentMap SEGMENTS[] = {
  // ── Singles ──────────────────────────────────────────────────────────────
  {15, 25, "S20"}, {18, 25, "S1"},  {19, 25, "S18"}, {21, 25, "S4"},
  {22, 25, "S13"}, {22, 32, "S6"},  {21, 32, "S10"}, {19, 32, "S15"},
  {18, 32, "S2"},  {15, 32, "S17"}, { 4, 32, "S3"},  { 5, 32, "S19"},
  {13, 32, "S7"},  {14, 32, "S16"}, {15, 12, "S8"},  {21, 12, "S11"},
  {14, 25, "S14"}, {13, 25, "S9"},  { 5, 25, "S12"}, { 4, 25, "S5"},
  // ── Doubles ──────────────────────────────────────────────────────────────
  {15, 23, "D20"}, {18, 23, "D1"},  {19, 23, "D18"}, {21, 23, "D4"},
  {22, 23, "D13"}, {22, 27, "D6"},  {21, 27, "D10"}, {19, 27, "D15"},
  {18, 27, "D2"},  {15, 27, "D17"}, { 4, 27, "D3"},  { 5, 27, "D19"},
  {13, 27, "D7"},  {14, 27, "D16"}, {18, 12, "D8"},  {22, 12, "D11"},
  {14, 23, "D14"}, {13, 23, "D9"},  { 5, 23, "D12"}, { 4, 23, "D5"},
  // ── Triples ──────────────────────────────────────────────────────────────
  {15, 26, "T20"}, {18, 26, "T1"},  {19, 26, "T18"}, {21, 26, "T4"},
  {22, 26, "T13"}, {22, 33, "T6"},  {21, 33, "T10"}, {19, 33, "T15"},
  {18, 33, "T2"},  {15, 33, "T17"}, { 4, 33, "T3"},  { 5, 33, "T19"},
  {13, 33, "T7"},  {14, 33, "T16"}, { 4, 12, "T8"},  {19, 12, "T11"},
  {14, 26, "T14"}, {13, 26, "T9"},  { 5, 26, "T12"}, { 4, 26, "T5"},
  // ── Bull ─────────────────────────────────────────────────────────────────
  {13, 12, "SB"},  // 25 outer bull
  { 5, 12, "DB"},  // 50 inner bull
  // ── Buttons ──────────────────────────────────────────────────────────────
  { 2,  4, "PLAYERBUTTON"},   // BTN_PLAYER  → joueur suivant
  { 2, 15, "BACKUPBUTTON"},   // BTN_DOUB    → annuler le tour
  { 2, 18, "GAMEBUTTON"},     // BTN_RESET   → quitter/menu
  { 2, 19, "MISSDART"},       // BTN_HOLD    → fléchette manquée
  { 2, 21, "GAMEBUTTON"},     // BTN_GAMES   → (même action que GAMEBUTTON)
  { 2, 22, "PLAYERBUTTON"},   // BTN_OPTIONS → (même action que PLAYERBUTTON)
};
const int NUM_SEGMENTS = sizeof(SEGMENTS) / sizeof(SEGMENTS[0]);

// ─── WebSocket ───────────────────────────────────────────────────────────────
WebSocketsClient wsClient;
bool wsConnected = false;

void onWsEvent(WStype_t type, uint8_t* payload, size_t length) {
  switch (type) {
    case WStype_CONNECTED:
      wsConnected = true;
      Serial.printf("[WS] Connected to pyDarts at %s:%d%s\n",
                    WS_HOST, WS_PORT, WS_PATH);
      break;
    case WStype_DISCONNECTED:
      wsConnected = false;
      Serial.println("[WS] Disconnected — will retry...");
      break;
    case WStype_ERROR:
      Serial.println("[WS] Error");
      break;
    default:
      break;
  }
}

void sendSegment(const char* segment) {
  if (!wsConnected) return;
  StaticJsonDocument<64> doc;
  doc["segment"] = segment;
  char buf[64];
  serializeJson(doc, buf);
  wsClient.sendTXT(buf);
  Serial.printf("[HIT] %s\n", buf);
}

// ─── Matrix scan ─────────────────────────────────────────────────────────────
const char* scanMatrix() {
  for (int m = 0; m < NUM_MASTERS; m++) {
    digitalWrite(masterPins[m], LOW);           // activate this column

    for (int s = 0; s < NUM_SLAVES; s++) {
      if (digitalRead(slavePins[s]) == LOW) {   // hit detected

        // Lookup segment name
        for (int i = 0; i < NUM_SEGMENTS; i++) {
          if (SEGMENTS[i].master == masterPins[m] &&
              SEGMENTS[i].slave  == slavePins[s]) {
            digitalWrite(masterPins[m], HIGH);  // deactivate before returning
            return SEGMENTS[i].segment;
          }
        }
        // Unknown intersection — log and ignore
        Serial.printf("[WARN] Unknown hit: master GPIO%d, slave GPIO%d\n",
                      masterPins[m], slavePins[s]);
      }
    }

    digitalWrite(masterPins[m], HIGH);          // deactivate this column
  }
  return nullptr;
}

// ─── Setup ───────────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  Serial.println("\n[BOOT] pyDarts ESP32 WiFi driver");

  // Configure matrix pins
  for (int m = 0; m < NUM_MASTERS; m++) {
    pinMode(masterPins[m], OUTPUT);
    digitalWrite(masterPins[m], HIGH);   // inactive by default
  }
  for (int s = 0; s < NUM_SLAVES; s++) {
    pinMode(slavePins[s], INPUT_PULLUP);
  }

  // Connect to WiFi
  Serial.printf("[WiFi] Connecting to %s", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.printf("\n[WiFi] Connected — IP: %s\n",
                WiFi.localIP().toString().c_str());

  // Connect to pyDarts WebSocket server
  wsClient.begin(WS_HOST, WS_PORT, WS_PATH);
  wsClient.onEvent(onWsEvent);
  wsClient.setReconnectInterval(3000);   // retry every 3s if disconnected
}

// ─── Loop ────────────────────────────────────────────────────────────────────
void loop() {
  wsClient.loop();   // handle WebSocket events & reconnection

  const char* segment = scanMatrix();
  if (segment != nullptr) {
    sendSegment(segment);
    delay(DEBOUNCE_MS);   // anti-rebond : ignorer les hits pendant DEBOUNCE_MS
  }
}
