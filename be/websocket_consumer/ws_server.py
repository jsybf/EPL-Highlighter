import logging

from websocket_server import WebsocketServer

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
logger.addHandler(console_handler)


class ChatWebSocketServer:
    def __init__(self, port: int):
        # config WebSocketServer class
        self.ws_server: WebsocketServer = WebsocketServer(port=port)
        self.ws_server.set_fn_client_left(self._client_left)
        self.ws_server.new_client(self._new_client)

    def _new_client(self, client):
        """call back func"""
        logging.debug(f"New client connected: {client['id']}")

    def _client_left(self, client):
        """call back func"""
        logging.debug(f"Client disconnected: {client['id']}")

    def run(self):
        """WebSocket 서버 실행."""
        logging.info("start websocket server")
        self.server.run_forever()
