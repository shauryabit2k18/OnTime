import pika
import time
import drowsiness
import multiprocessing
from threading import Thread
import sys
# t = Thread(target=drowsiness.track() )
# t.daemon = True
# t.start()
# t.join()


class alert(Thread):
    def run(self):
        connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.queue_declare(queue='hello')
        channel.queue_declare(queue='website')


        def callback(ch, method, properties, body):
            print(" [x] Received {} {}".format(body,time.time()), flush=True)


        channel.basic_consume(
            queue='website', on_message_callback=callback, auto_ack=True)


        channel.basic_consume(
            queue='drowsiness', on_message_callback=callback, auto_ack=True)


        print(' [*] Waiting for messages. To exit press CTRL+C', flush=True)
        channel.start_consuming()


t1 = alert()
t2 = drowsiness.track()

t1.start()
t2.start()

