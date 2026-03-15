#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import json
import queue
import socket
import threading

try:
    import websockets
except ImportError:
    websockets = None

try:
    from zeroconf import ServiceInfo, Zeroconf
    ZEROCONF_AVAILABLE = True
except ImportError:
    ZEROCONF_AVAILABLE = False


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
        self._client_count = 0
        self._zeroconf = None
        self._mdns_info = None

    def start(self):
        if websockets is None:
            self.Logs.Log("FATAL", "websockets library not installed. Run: pip install websockets")
            return False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self.Logs.Log("DEBUG", "WiFi WebSocket server started on port {}".format(self.port))
        self._start_mdns()
        return True

    def _get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"
        finally:
            s.close()

    def _start_mdns(self):
        if not ZEROCONF_AVAILABLE:
            self.Logs.Log("WARNING", "zeroconf not installed — mDNS disabled. Run: pip install zeroconf")
            return
        try:
            ip = self._get_local_ip()
            self._zeroconf = Zeroconf()
            self._mdns_info = ServiceInfo(
                "_pydarts._tcp.local.",
                "pyDarts._pydarts._tcp.local.",
                addresses=[socket.inet_aton(ip)],
                port=self.port,
                properties={"version": "1.0"},
            )
            self._zeroconf.register_service(self._mdns_info)
            self.Logs.Log("DEBUG", "mDNS: pyDarts advertised at {}:{} (_pydarts._tcp)".format(ip, self.port))
        except Exception as e:
            self.Logs.Log("WARNING", "mDNS advertisement failed: {}".format(e))

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
        self._client_count += 1
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
        finally:
            self._client_count -= 1

    def is_connected(self):
        """Returns True if at least one ESP32 client is connected."""
        return self._client_count > 0

    def read(self):
        """Non-blocking read. Returns segment string or False."""
        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return False

    def stop(self):
        if self._zeroconf and self._mdns_info:
            try:
                self._zeroconf.unregister_service(self._mdns_info)
                self._zeroconf.close()
            except Exception:
                pass
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
