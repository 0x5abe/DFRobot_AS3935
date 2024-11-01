#!/usr/bin/env python
import rabbitpy, sys, os, json

EXCHANGE = ''
ROUTING_KEY = 'lightning_data'

def main():
    with rabbitpy.Connection() as connection:

      with connection.channel() as channel:
          # Declare the queue
          queue = rabbitpy.Queue(channel, QUEUE)
          queue.declare()

          # Bind the queue to the exchange
          queue.bind(EXCHANGE, ROUTING_KEY)

    with connection.channel() as channel:
        for message in rabbitpy.Queue(channel, QUEUE).consume_messages():
            print(message.body)
            message.ack()
            received += 1

    print(' [*] Waiting for messages. To exit press CTRL+C')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)