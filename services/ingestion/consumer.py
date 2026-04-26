# opens websocket connection and keeps connection alive. waits for live events to occur and parses from json

import json
import websocket
from services.ingestion.config import *


class WSconsumer:

    def __init__(self, on_event, jetstream_index=0):
        self.on_event = on_event
        self.jetstream_url = JETSTREAM_URLS[jetstream_index]

    def _on_open(self, ws):
        print("Connected to Bluesky Jetstream")

    def _on_message(self, ws, message):
        try:
            event = json.loads(message)
        except json.JSONDecodeError:
            return

        self.on_event(event, ws)

    def _on_error(self, ws, error):
        print("WebSocket error:", error)

    def _on_close(self, ws, close_status_code, close_msg):
        print("Connection closed:", close_status_code, close_msg)

    # Actual WebSocket Connection
    def run(self):
        ws = websocket.WebSocketApp(
            self.jetstream_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        ws.run_forever()
