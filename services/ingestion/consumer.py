#-----------------------------------------------------
#  Consumer class opens a live websocket connection. 
#  It receives raw JSON events from bluesky and passes back the event.  
# 
#   --- Fault Tolerance ---
#  The WebSocket connection to Bluesky can drop due to network fails, remote services restarts, timeouts
#   if reconnection fails, increase the wait time before reattempting. Avoids hammering Bluesky with reconnect attempts
#   and keeps ingestion container alive. Once it does connect the the time delay resets.

#  --- Availibility ---
#  if one Bluesky Jetstream endpoint is unhealthy, the service can try another server endpoint.
#  instead of retrying the same one forever. prevents the service from getting stuck on one unhealthy regional server.
# 
#-----------------------------------------------------

import json
import time
import websocket
from services.ingestion.config import *
from services.logging_utils import get_logger

logger = get_logger("services.ingestion.consumer")

class WSconsumer:

    def __init__(self, on_event, jetstream_index=0):
        self.on_event = on_event
        self.jetstream_index = jetstream_index
        self.jetstream_url = JETSTREAM_URLS[self.jetstream_index]
        self.failed_reconnect_attempts = 0
        self.stop_requested = False
        self.connected = False
        self.connected_once = False

    # Succesful connection
    def _on_open(self, ws):
        self.connected = True
        self.connected_once = True
        logger.info("Connected to Bluesky Jetstream: %s", self.jetstream_url)

    # handles the event message
    def _on_message(self, ws, message):
        try:
            event = json.loads(message)
        except json.JSONDecodeError:
            return
        self.on_event(event, ws)

    # error handle
    def _on_error(self, ws, error):
        logger.error("WebSocket error: %s", error)

    # close websocker connection
    def _on_close(self, ws, close_status_code, close_msg):
        self.connected = False
        logger.warning(
            "Connection closed: status=%s message=%s",
            close_status_code,
            close_msg,
        )

    # switch server
    def _switch_jetstream_server(self):
        self.jetstream_index = (self.jetstream_index + 1) % len(JETSTREAM_URLS)
        self.jetstream_url = JETSTREAM_URLS[self.jetstream_index]
        self.failed_reconnect_attempts = 0

        logger.warning(
            "Switching to Jetstream server index=%s url=%s",
            self.jetstream_index,
            self.jetstream_url,
        )

    # Run Actual WebSocket Connection
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
            ws.run_forever()                    # keep connection alive

            if self.stop_requested:
                break

            if self.connected_once:
                reconnect_delay = RECONNECT_DELAY_SECONDS
                self.failed_reconnect_attempts = 0
            else:                                           # counter to try other server
                self.failed_reconnect_attempts += 1

                if self.failed_reconnect_attempts >= MAX_RECONNECT_ATTEMPTS_BEFORE_SWITCH:
                    self._switch_jetstream_server()

            logger.warning(
                "Jetstream disconnected. Reconnecting in %.1f seconds...",
                reconnect_delay,
            )

            time.sleep(reconnect_delay)
            
            #reconnect with increasing time delay
            reconnect_delay = min(                      
                reconnect_delay * RECONNECT_BACKOFF_MULTIPLIER,
                MAX_RECONNECT_DELAY_SECONDS,
            )

    def stop(self):
        self.stop_requested = True
        logger.info("Stop requested for Jetstream consumer.")
