import os
import urlparse
# import json
from rq import Queue
from redis import Redis
from service_utils import compress
from pubnub import Pubnub


def setup_queue():
    redis_url = os.getenv('REDIS_URL')
    if not redis_url:
        raise RuntimeError('Set up Redis first.')

    urlparse.uses_netloc.append('redis')
    url = urlparse.urlparse(redis_url)
    conn = Redis(host=url.hostname, port=url.port, db=0, password=url.password)

    q = Queue('default', connection=conn)
    return q


def publish_error(msg):
    pubnub = Pubnub(
        publish_key=os.getenv('PUBLISH_KEY'),
        subscribe_key=os.getenv('SUBSCRIBE_KEY'),
        pooling=False
    )
    service_channel = 'service_channel'
    pubnub.publish(service_channel, msg)


def callback(message, channel):
    q = setup_queue()
    try:
        data = message
        case_id = data.get('id', None)
        file_list = data.get('files', None)
        bucket_name = data.get('bucket', None)
        base_name = data.get('prefix', None)

        if case_id is not None and file_list is not None and bucket_name is not None:
            q.enqueue(compress.process_data, case_id, file_list, bucket_name, base_name)
        else:
            publish_error('Invalid data')
    except (ValueError, UnicodeDecodeError):
        publish_error('Error processing data')
    print message


def error(message):
    print("ERROR : " + str(message))


def connect(message):
    print("CONNECTED")


def reconnect(message):
    print("RECONNECTED")


def disconnect(message):
    print("DISCONNECTED")


pubnub = Pubnub(
    publish_key=os.getenv('PUBLISH_KEY'),
    subscribe_key=os.getenv('SUBSCRIBE_KEY'),
)
channel = 'service_channel'
pubnub.subscribe(channel, callback=callback, error=error,
                 connect=connect, reconnect=reconnect, disconnect=disconnect)
