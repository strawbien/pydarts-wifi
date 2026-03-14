#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import json
import queue
import threading

try:
    import websockets
except ImportError:
    websockets = None


class WifiDriver:
    """
    WebSocket server that receives dart hits from an ESP32.
    ESP32 sends JSON messages: {"segment": "T20"}
    Segment names are put into a queue for CInput to consume.
    """

    def __init__(self, Logs, port=8000):
        self.Logs = Logs
        self.port = port
        self._queue = queue.Queue()
        self._thread = None
        self._loop = None

    def start(self):
        if websockets is None:
            self.Logs.Log("FATAL", "websockets library not installed. Run: pip install websockets")
            return False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self.Logs.Log("DEBUG", "WiFi WebSocket server started on port {}".format(self.port))
        return True

    def _run(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._serve())

    async def _serve(self):
        async with websockets.serve(self._handler, "0.0.0.0", self.port):
            self.Logs.Log("DEBUG", "WebSocket listening on 0.0.0.0:{}".format(self.port))
            await asyncio.Future()  # run forever

    async def _handler(self, websocket):
        addr = websocket.remote_address
        self.Logs.Log("DEBUG", "ESP32 connected from {}".format(addr))
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    segment = data.get("segment", "").upper()
                    if segment:
                        self._queue.put(segment)
                        self.Logs.Log("DEBUG", "WiFi hit: {}".format(segment))
                except (json.JSONDecodeError, AttributeError):
                    self.Logs.Log("DEBUG", "WiFi invalid message: {}".format(message))
        except Exception as e:
            self.Logs.Log("DEBUG", "ESP32 disconnected ({}): {}".format(addr, e))

    def read(self):
        """Non-blocking read. Returns segment string or False."""
        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return False

    def stop(self):
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
