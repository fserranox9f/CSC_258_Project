import json
import websocket
import time
from config import JETSTREAM_URL

class BlueskyConsumer:
    def __init__(self, on_event):
        self.on_event = on_event

    def _on_open(self, ws):
        print("Connected to Bluesky Jetstream")

    def _on_message(self, ws, message):
        try:
            event = json.loads(message)
        except json.JSONDecodeError:
            print("Skipping invalid JSON")
            return

        try:
            self.on_event(event, ws)
        except Exception as e:
            print("Error in event handler:", e)

    def _on_error(self, ws, error):
        print("WebSocket error:", error)

    def _on_close(self, ws, close_status_code, close_msg):
        print(f"Connection closed: {close_status_code} - {close_msg}")

    def run(self):
        while True:
            try:
                ws = websocket.WebSocketApp(
                    JETSTREAM_URL,
                    on_open=self._on_open,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close,
                )

                ws.run_forever()
            except Exception as e:
                print("Reconnecting in 5 seconds...", e)
                time.sleep(5)