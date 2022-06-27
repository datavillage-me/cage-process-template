import dv_tools
import process
import logging
import os

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO')
logging.basicConfig(filename='listener.log', level=LOGLEVEL, format='%(asctime)s - %(levelname)s - %(message)s')

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

