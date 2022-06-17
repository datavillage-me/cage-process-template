import rdflib
import requests
import redis
import time
import os
import json

DEBUG = os.environ.get('DEBUG', '').lower() == 'true'


class Client:
    """
    Remote HTTP client that helps accessing the Datavillage service APIs.
    It is instanciated for a given client and application.
    """
    def __init__(self, token: str = None, app_id: str = None, client_id: str = None, base_url: str = None):
        token = token if token is not None else os.environ.get("DV_TOKEN")
        app_id = app_id if app_id is not None else os.environ.get("DV_APP_ID")
        client_id = client_id if client_id is not None else os.environ.get("DV_CLIENT_ID")
        base_url = base_url if base_url is not None else os.environ.get("DV_URL")

        self.token: str = token
        self.appId: str = app_id
        self.clientId: str = client_id
        self.baseUrl: str = base_url

    def getUsers(self):
        """
        Returns the list of active users for this application
        """
        userIds = self.request(f'/clients/{self.clientId}/applications/{self.appId}/activeUsers')

        return userIds

    def getData(self, userId: str, format: str = 'turtle'):
        """
        Returns the available data for a given user.
        If the format is turtle (default), the returned value is an rdflib graph.
        """
        raw_data = self.request(f'/clients/{self.clientId}/applications/{self.appId}/activeUsers/{userId}/data')
        if (format == 'turtle'):
            rdf_data = rdflib.Graph()
            rdf_data.parse(data=raw_data, format=format)
            return rdf_data
        else:
            # Currently no other format than turtle is supported
            raise Exception(f'Unknown format {format}')

    def request(self, path: str):
        url = f'{self.baseUrl}{path}'
        if DEBUG:
            print(f'[HTTP GET] {url}')

        resp = requests.get(url, headers={"Authorization":f"Bearer {self.token}"})
        if not resp.ok:
            raise Exception(f'DV Request failed on {path}: {resp.text}')

        if resp.headers['Content-Type'] == 'application/json':
            return resp.json()
        else:
            return resp.text


class RedisQueue:
    """
    Client to the local redis queue exposed in the cage.
    """
    def __init__(self, host=None, port=None):
        host = host if host is not None else os.environ.get("REDIS_SERVICE_HOST")
        port = port if port is not None else os.environ.get("REDIS_SERVICE_PORT")

        self.redis = redis.Redis(host, port, db=0) if port is not None else redis.Redis(host, db=0)
        self.pubsub = self.redis.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe("dv")

    def listenOnce(self, timeout=120):
        """
        Listen to the redis queue until one message is obtained, or timeout is reached
        :param timeout: timeout delay in seconds
        :return: the received message, or None
        """
        stop_time = time.time() + timeout

        # there is a bug in the redis-py client, causing get_message to return None for subscribe messages when a timeout
        # argument is given, regardless of 'ignore_subscribe_messages'. (cf https://github.com/redis/redis-py/issues/733)
        # work around this by listening until a truthy object is returned, or stop_time is reached
        while time.time() < stop_time:
            message = self.pubsub.get_message(timeout=stop_time - time.time())
            if message:
                if DEBUG:
                    print(f'Received message...')
                break
        evt = json.loads(message.get('data'))
        return evt

    def listen(self, processor, timeout=3600):
        """
        Listen to the redis queue until the timeout is reached, and process every incoming message in that interval
        with the provided processor function
        :param processor: the function to process incoming messages
        :param timeout: timeout in seconds
        :return:
        """
        stop_time = time.time() + timeout

        # there is a bug in the redis-py client, causing get_message to return None for subscribe messages when a timeout
        # argument is given, regardless of 'ignore_subscribe_messages'. (cf https://github.com/redis/redis-py/issues/733)
        # work around this by listening until a truthy object is returned, or stop_time is reached
        while time.time() < stop_time:
            if DEBUG:
                print(f'Waiting for message...')
            message = self.pubsub.get_message(timeout=stop_time - time.time())
            if message:
                if DEBUG:
                    print(f'Processing message...')
                evt = json.loads(message.get('data'))
                processor(evt)
