import json
import logging
from typing import Callable

from kafka import KafkaConsumer

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
logger.addHandler(console_handler)


def get_kafka_consumer(broker_host: str, topic: str) -> KafkaConsumer:
    return KafkaConsumer(
        topic,
        bootstrap_servers=broker_host,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="test-group",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),  # 메시지 디코딩
    )


def main_loop(broker_host: str, topic: str, send_message_to_all: Callable[[str], None]):
    # get kafka consumer
    consumer: KafkaConsumer = get_kafka_consumer(broker_host, topic)
    logging.info(f"connected to kafka broker host:[{broker_host}] topic:[{topic}]")

    # main loop
    for message in consumer:
        logging.debug(f'consumed message: ${message}')

        # send socket
        message_str: str = json.dumps(message)
        send_message_to_all(message)
