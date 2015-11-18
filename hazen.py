#!/usr/bin/env python

import random
import string
import sys
import time
from argparse import ArgumentParser
from timeit import default_timer

import pika


def die_error(msg):
    print "ERROR: %s" % msg
    sys.exit(1)


def generate_payloads(num_payloads, min_size, max_size):
    result = list()
    for i in xrange(0, num_payloads):
        sz = random.randrange(min_size, max_size)
        msg = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(sz))
        result.append(msg)
    return result


def publish(chan, opts):
    # Pre-generate all msg payloads to save time in the send loop.
    payloads = generate_payloads(opts.msg_per_second, opts.min_msg_size, opts.max_msg_size)
    exch = opts.exchange or ''
    key = opts.routing_key or ''

    interval_ts = default_timer()
    avg_msgs_per_sec = 0.0
    total_msgs = 0

    while True:
        start_ts = default_timer()
        last_msg_count = 0
        early_out = False
        for i in xrange(0, opts.msg_per_second):
            msg = random.choice(payloads)
            chan.basic_publish(exchange=exch, routing_key=key, body=msg)

            last_msg_count = i
            total_msgs += 1

            if (default_timer() - start_ts) > 1.0:
                # We've published as much as we can, so stop here.
                early_out = True
                break

        # Did we publish all messages before 1 second elapsed?  If so, we need to sleep for
        # the amount of time left.
        if not early_out:
            delta_ts = default_timer() - start_ts
            time.sleep(float(delta_ts))

        avg_msgs_per_sec = (avg_msgs_per_sec + float(last_msg_count - avg_msgs_per_sec) / total_msgs)
        if (default_timer() - interval_ts) > 60.0:
            print "** total msgs sent: %d, last sent: %d, avg_per_sec: %.2f" \
                  % (total_msgs, last_msg_count, avg_msgs_per_sec)
            interval_ts = default_timer()


consumed_count = 0


def _consumer_callback(ch, method, properties, body):
    global consumed_count
    consumed_count += 1
    if consumed_count % 5000 == 0:
        print "Consumed %d messages." % consumed_count


def consume(chan, opts):
    if opts.prefetch:
        chan.basic_qos(prefetch_count=opts.prefetch)

    chan.basic_consume(_consumer_callback,
                       queue=opts.queue,
                       no_ack=True)

    print "Starting consumer..."
    chan.start_consuming()


if __name__ == '__main__':
    parser = ArgumentParser(description='Testing RabbitMQ')
    parser.add_argument('-r', dest='rabbit_addr', default="localhost",
                        help="Address of Rabbit server.  In host or host:port form.")

    parser.add_argument('-e', dest='exchange',
                        help="Name of the exchange to use for publish/consume, if any.")

    parser.add_argument('-p', dest='publisher', action='store_true', default=False,
                        help="Run in PUBLISHER mode.")
    parser.add_argument('-k', dest='routing_key',
                        help="Routing key to use when publishing, if any.")
    parser.add_argument('-mps', dest='msg_per_second', type=int,
                        help="The number of messages to publish per second.")
    parser.add_argument('-mmin', dest='min_msg_size', default=256, type=int,
                        help="The minimum size of single message to publish.")
    parser.add_argument('-mmax', dest='max_msg_size', default=2048, type=int,
                        help="The maximum size of a single message to publish.")

    parser.add_argument('-c', dest='consumer', action='store_true', default=False,
                        help="Run in CONSUMER mode.")
    parser.add_argument('-q', dest='queue',
                        help="Name of the queue to use when consuming, if any.")
    parser.add_argument('-pfc', dest='prefetch', type=int,
                        help="Prefetch count to use when consuming.")

    opts = parser.parse_args()

    if not opts.publisher and not opts.consumer:
        die_error("Specify a mode - publisher or consumer.")

    if opts.publisher:
        if not opts.msg_per_second or opts.msg_per_second < 1:
            die_error("A value for msg_per_second is required for publishing.")

    try:
        if ':' in opts.rabbit_addr:
            pair = opts.rabbit_addr.split(':')
            params = pika.ConnectionParameters(host=pair[0], port=int(pair[1]))
        else:
            params = pika.ConnectionParameters(host=opts.rabbit_addr)

        conn = pika.BlockingConnection(params)
        chan = conn.channel()

        if opts.publisher:
            publish(chan, opts)
        else:
            if not opts.queue:
                die_error("A queue name is required for consuming.")

            consume(chan, opts)
    finally:
        conn.close()
