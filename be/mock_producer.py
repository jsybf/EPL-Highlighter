import dataclasses
import json
import logging
import time
from datetime import datetime

from kafka import KafkaProducer

from common.kafka.dto.chat_message import ChatMessage

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def main(broker_host: str, topic: str, sleep_sec: int = 1):
    producer = KafkaProducer(
        bootstrap_servers=broker_host,
        value_serializer=lambda chat_model: json.dumps(
            dataclasses.asdict(chat_model)
        ).encode("utf-8"),
    )

    while True:
        time.sleep(sleep_sec)
        message = ChatMessage(
            source_id='mock_source_id',
            source_type='mock_type',
            time=datetime.now().isoformat(),
            author='mock_author',
            message='mock_message'
        )
        logger.debug("send mock ChatMessage")
        producer.send(value=message, topic=topic)


if __name__ == "__main__":
    main(
        broker_host='localhost:19092',
        topic='epl',
        sleep_sec=1
    )
