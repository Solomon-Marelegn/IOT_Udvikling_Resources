import network
from machine import Pin
from simple import MQTTClient
import time

class MQTT_Publisher():
    def __init__(self, broker, client_id, topic):
        self.broker = broker
        self.client_id = client_id
        self.topic = topic
        self.client = self.connect()

    def connect(self):
        client = MQTTClient(self.client_id, self.broker, keepalive=0)
        try:
            client.connect()
            print(f'Connected to {self.broker} MQTT Broker')
        except Exception as e:
            print('Connection to MQTT Broker failed. Will retry. Error:', str(e))
            client = None
        return client

    def publish(self, message):
        try:
            self.client.publish(self.topic, message)
            return True
        except Exception as e:
            print('Failed to publish message. Reconnecting. Error:', str(e))
            self.client = self.connect()
            if self.client:
                self.client.publish(self.topic, message)
            return False


