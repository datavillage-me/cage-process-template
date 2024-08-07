"""
Unit test.
"""

# Read env variables from a local .env file, to fake the variables normally provided by the cage container
import dotenv
dotenv.load_dotenv('.env')
import unittest
import logging
import process

class Test(unittest.TestCase):
    # def test_data_quality_check(self):
    #     """
    #     Try the process  without going through the redis queue
    #     """
    #     test_event = {
    #         'type': 'CHECK_DATA_QUALITY'
    #     }

    #     process.event_processor(test_event)
    
    def test_common_customers_demo(self):
        """
        Try the process  without going through the redis queue
        """
        test_event = {
            'type': 'CHECK_COMMON__DEMO_CUSTOMERS'
        }
        
        process.event_processor(test_event)

    # def test_process_queue_once(self):
    #     """
    #     Try the process by sending an event to the queue and consume exactly one event.
    #     """

    #     test_event = {
    #         'userIds': [os.environ["TEST_USER"]],
    #         'trigger': 'full',
    #         # 'jobId': None,
    #     }

    #     r = RedisQueue()

    #     # fake the publishing of an event
    #     r.redis.publish("dv", json.dumps(test_event))

    #     # wait for exactly one event and process it
    #     event = r.listenOnce()
    #     process.event_processor(event)

    # def test_process_queue_loop(self):
    #     """
    #     Try the process by sending an event to the queue and let the queue loop in wait.
    #     """

    #     test_event = {
    #         'userIds': [os.environ["TEST_USER"]],
    #         'trigger': 'full',
    #         # 'jobId': None,
    #     }

    #     r = RedisQueue()

    #     # fake the publishing of an event
    #     r.redis.publish("dv", json.dumps(test_event))

    #     # let the queue wait for events and dispatch them to the process function
    #     r.listen(process.event_processor, 2)