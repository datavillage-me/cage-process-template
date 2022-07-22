import logging
import os

import dv_tools
import process

LOGLEVEL = os.environ.get("LOGLEVEL", "INFO")
# let the log go to stdout, as it will be captured by the cage operator
logging.basicConfig(
    level=LOGLEVEL, format="%(asctime)s - %(levelname)s - %(message)s"
)  # filename='listener.log'
logging.getLogger().addHandler(logging.StreamHandler())

DAEMON = False

# Instantiate the local Datavillage Redis queue
rq = dv_tools.RedisQueue()

if DAEMON:
    # listen continously and process all incoming events
    # the listen loop stops by default after 1h
    rq.listen(process.processEvent)
else:
    # wait for one event and process it
    event = rq.listenOnce()
    if event:
        process.processEvent(event)
