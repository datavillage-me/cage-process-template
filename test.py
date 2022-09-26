# this code can be tested in a local environment
# for this, start a local redis server and set the appropriate variables in .env.test

# Read env variables from a local .env file, to fake the variables normally provided by the cage container
import dotenv
dotenv.load_dotenv('.env.test')
import os
import unittest
import process
import json
import logging
from dv_utils import RedisQueue

DEBUG = os.environ.get('DEBUG', '').lower() == 'true'
logging.basicConfig(filename='events.log', level=logging.DEBUG if DEBUG else logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

class Test(unittest.TestCase):

    def test_process(self):
        """
        Try the process on a single user configured in the test .env file, without going through the redis queue
        """
        test_event = {
            'userIds': [os.environ["TEST_USER"]],
            'trigger': 'full',
            # 'jobId': None,
        }

        process.event_processor(test_event)

    def test_process_queue_once(self):
        """
        Try the process by sending an event to the queue and consume exactly one event.
        """

        test_event = {
            'userIds': [os.environ["TEST_USER"]],
            'trigger': 'full',
            # 'jobId': None,
        }

        r = RedisQueue()

        # fake the publishing of an event
        r.redis.publish("dv", json.dumps(test_event))

        # wait for exactly one event and process it
        event = r.listenOnce()
        process.event_processor(event)

    def test_process_queue_loop(self):
        """
        Try the process by sending an event to the queue and let the queue loop in wait.
        """

        test_event = {
            'userIds': [os.environ["TEST_USER"]],
            'trigger': 'full',
            # 'jobId': None,
        }

        r = RedisQueue()

        # fake the publishing of an event
        r.redis.publish("dv", json.dumps(test_event))

        # let the queue wait for events and dispatch them to the process function
        r.listen(process.event_processor, 2)
