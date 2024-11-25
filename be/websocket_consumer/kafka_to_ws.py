import json
import logging
from typing import Callable

from kafka import KafkaConsumer

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_kafka_consumer(broker_host: str, topic: str) -> KafkaConsumer:
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=broker_host,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="test-group",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),  # 메시지 디코딩
    )

    logger.info(f"connected to kafka broker host:[{broker_host}] topic:[{topic}]")

    return consumer


def main_loop(consumer: KafkaConsumer, send_message_to_all: Callable[[str], None]):
    # main loop
    for record in consumer:
        message = record.value
        logger.debug(f'consumed message: ${message}')

        # send socket
        message_str: str = json.dumps(message)
        send_message_to_all(message_str)
