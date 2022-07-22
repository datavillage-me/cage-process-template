import json
import logging
import os
import time
from typing import Literal

import rdflib
import redis
import requests


class Client:
    """
    Remote HTTP client that helps accessing the Datavillage service APIs.
    It is instanciated for a given client and application.
    """

    def __init__(
        self,
        token: str = None,
        app_id: str = None,
        client_id: str = None,
        base_url: str = None,
    ):
        token = token if token is not None else os.environ.get("DV_TOKEN")
        app_id = app_id if app_id is not None else os.environ.get("DV_APP_ID")
        client_id = (
            client_id if client_id is not None else os.environ.get("DV_CLIENT_ID")
        )
        base_url = base_url if base_url is not None else os.environ.get("DV_URL")

        self.token: str = token
        self.appId: str = app_id
        self.clientId: str = client_id
        self.baseUrl: str = base_url

    def getUsers(self):
        """
        Returns the list of active users for this application
        """
        userIds = self.request(
            f"/clients/{self.clientId}/applications/{self.appId}/activeUsers"
        )

        return userIds

    def getData(self, userId: str, format: str = "turtle"):
        """
        Returns the available data for a given user.
        If the format is turtle (default), the returned value is an rdflib graph.
        """
        raw_data = self.request(
            f"/clients/{self.clientId}/applications/{self.appId}/activeUsers/{userId}/data"
        )
        if format == "turtle":
            rdf_data = rdflib.Graph()
            rdf_data.parse(data=raw_data, format=format)
            return rdf_data
        else:
            # Currently no other format than turtle is supported
            raise Exception(f"Unknown format {format}")

    def writeResults(self, userId: str, filename: str, content: str):
        """
        Writes the results into the pod.
        """

        # currently only 'inferences' and 'explains' are supported
        if not filename in ["inferences", "explains"]:
            raise Exception("Unsupported result file name: " + filename)

        self.request(
            f"/clients/{self.clientId}/applications/{self.appId}/activeUsers/{userId}/{filename}",
            method="PUT",
            data=content,
        )

    def request(
        self,
        path: str,
        method: Literal["GET", "POST", "PUT", "DELETE"] = "GET",
        format: str = None,
        data=None,
    ):
        url = f"{self.baseUrl}{path}"
        logging.debug(f"[HTTP {method}] {url}")

        headers = {"Authorization": f"Bearer {self.token}"}
        if format:
            headers["Content-Type"] = format

        resp = requests.request(method, url, headers=headers, data=data)
        if not resp.ok:
            raise Exception(f"DV Request failed on {path}: {resp.text}")

        if resp.headers["Content-Type"] == "application/json":
            return resp.json()
        else:
            return resp.text


class RedisQueue:
    """
    Client to the local redis queue exposed in the cage.
    """

    def __init__(self, host=None, port=None, consumer_name="consummer-0"):
        host = host if host is not None else os.environ.get("REDIS_SERVICE_HOST")
        port = port if port is not None else os.environ.get("REDIS_SERVICE_PORT")

        self.consumer_name = consumer_name
        self.redis = (
            redis.Redis(host, port, db=0)
            if port is not None
            else redis.Redis(host, db=0)
        )

    def listenOnce(self, timeout=120):
        """
        Listen to the redis queue until one message is obtained, or timeout is reached
        :param timeout: timeout delay in seconds
        :return: the received message, or None
        """
        messages = self.redis.xreadgroup(
            "consummers",
            self.consumer_name,
            {"events": ">"},
            noack=True,
            count=1,
            block=timeout * 1000,
        )
        if messages:
            message = [
                json.loads(msg_data) | {"msg_id": msg_id.decode()}
                for msg_id, msg_data in messages[0][1]
            ][0]
            msg_id = message["msg_id"]
            logging.debug(f"Received message {msg_id}...")
            return message
        return None

    def listen(self, processor, timeout=3600):
        """
        Listen to the redis queue until the timeout is reached, and process every incoming message in that interval
        with the provided processor function
        :param processor: the function to process incoming messages
        :param timeout: timeout in seconds
        :return:
        """
        evt = self.listenOnce(timeout)
        if evt:
            processor(evt)
