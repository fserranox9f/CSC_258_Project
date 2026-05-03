# opens websocket connection and keeps connection alive. waits for live events to occur and parses from json

import json
import time
import websocket
from services.ingestion.config import *
from services.logging_utils import get_logger


logger = get_logger("services.ingestion.consumer")


class WSconsumer:

    def __init__(self, on_event, jetstream_index=0):
        self.on_event = on_event
        self.jetstream_url = JETSTREAM_URLS[jetstream_index]
        self.stop_requested = False
        self.connected = False
        self.connected_once = False

    def _on_open(self, ws):
        self.connected = True
        self.connected_once = True
        logger.info("Connected to Bluesky Jetstream: %s", self.jetstream_url)

    def _on_message(self, ws, message):
        try:
            event = json.loads(message)
        except json.JSONDecodeError:
            return

        self.on_event(event, ws)

    def _on_error(self, ws, error):
        logger.error("WebSocket error: %s", error)

    def _on_close(self, ws, close_status_code, close_msg):
        self.connected = False
        logger.warning(
            "Connection closed: status=%s message=%s",
            close_status_code,
            close_msg,
        )

    # Actual WebSocket Connection
    def run(self):
        reconnect_delay = RECONNECT_DELAY_SECONDS

        while not self.stop_requested:
            ws = websocket.WebSocketApp(
                self.jetstream_url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
            )

            self.connected = False
            self.connected_once = False
            ws.run_forever()

            if self.stop_requested:
                break

            if self.connected_once:
                reconnect_delay = RECONNECT_DELAY_SECONDS

            logger.warning(
                "Jetstream disconnected. Reconnecting in %.1f seconds...",
                reconnect_delay,
            )
            time.sleep(reconnect_delay)
            reconnect_delay = min(
                reconnect_delay * RECONNECT_BACKOFF_MULTIPLIER,
                MAX_RECONNECT_DELAY_SECONDS,
            )

    def stop(self):
        self.stop_requested = True
        logger.info("Stop requested for Jetstream consumer.")
