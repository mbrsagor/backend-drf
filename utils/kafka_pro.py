from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def place_order(order):
    # 1. Save order
    save_to_db(order)

    # 2. Publish an event instead of calling the 4 services
    producer.send("orders", order)

    # 3. Immediately return
    return "Order Accepted."
