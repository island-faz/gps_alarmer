#!/usr/bin/env python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

#channel.queue_declare(queue='test2')

coord = '{"x": "-5.2294922", "y": "33.2846200", "speed":"50.5"}'

coord_o = '{"x": "-3.6035156", "y": "27.1764691", "speed":"50"}'

channel.basic_publish(exchange='', routing_key='hello', body=coord_o)

connection.close()
