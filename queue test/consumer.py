import rabbitpy
import json

EXCHANGE = ''
ROUTING_KEY = 'lightning_data'
QUEUE = 'lightning_queue'

with rabbitpy.Connection() as conn:
    with conn.channel() as channel:
        queue = rabbitpy.Queue(channel, QUEUE)
        queue.declare()
        queue.bind(EXCHANGE, ROUTING_KEY)

        # Exit on CTRL-C
        try:
            # Consume the message
            for message in queue:
                print(json.loads(message.body))
                message.ack()

        except KeyboardInterrupt:
            print('Exited consumer')