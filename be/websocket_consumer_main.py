import logging
import os
import threading

from dotenv import load_dotenv

from websocket_consumer import main_loop, ChatWebSocketServer, get_kafka_consumer

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



def app(ws_port: int, kafka_host: str, kafka_topic: str):
    # start websocket server
    ws_server = ChatWebSocketServer(port=ws_port)
    ws_thread = threading.Thread(target=ws_server.run, daemon=True)
    ws_thread.start()

    # connect kafka
    consumer = get_kafka_consumer(kafka_host, kafka_topic)

    # start main loop
    main_loop(consumer,  ws_server.ws_server.send_message_to_all)


if __name__ == '__main__':
    # load env
    load_dotenv(dotenv_path='./.websocket_consumer.env')

    ws_port: int = int(os.getenv('WS_PORT'))
    kafka_host: str = os.getenv('KAFKA_HOST')
    kafka_topic: str = os.getenv('KAFKA_TOPIC')

    logger.info(f"""
        -----env loaded-----
        ws_port={ws_port} 
        kafka_host={kafka_host}
        kafka_topic={kafka_topic}
    """)

    # start server
    app(ws_port, kafka_host, kafka_topic)
