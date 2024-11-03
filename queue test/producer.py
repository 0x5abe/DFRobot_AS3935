import rabbitpy
import json
import datetime
import time
from datetime import datetime

EXCHANGE = ''
ROUTING_KEY = 'lightning_data'

with rabbitpy.Connection() as connection:
    with connection.channel() as channel:
        while True:
            message = {
                "message": 'This is a test message!',
                "distance": 'A lot!',
                "intensity": 'Hella!',
                "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
            }
            messageToSend = rabbitpy.Message(channel, json.dumps(message))
            messageToSend.publish(EXCHANGE, ROUTING_KEY)

            print('Message sent!')
            time.sleep(1.0)