import logging
import time

import dv_tools

logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())


def processEvent(evt):
    """
    Process an incoming event
    """
    start = time.time()

    try:
        logging.info(f"Processing event {evt}")

        client = dv_tools.Client()

        # Use userIds provided in the event, or get all active users for this application
        user_ids = evt.get("userIds") if "userIds" in evt else client.getUsers()

        logging.info(f"Processing {len(user_ids)} users")
        for userId in user_ids:
            try:
                # retrieve data graph for user
                user_data = client.getData(userId)

                logging.info(f"{len(user_data)} statements for user {userId}")

                # for the sake of this example, write some RDF with the number of user statements into the user's pod
                client.writeResults(
                    userId,
                    "inferences",
                    f"<https://datavillage.me/{userId}> <https://datavillage.me/count> {len(user_data)}",
                )
            except Exception as err:
                logging.warning(f"Failed to process user {userId} : {err}")
    except Exception as err:
        logging.error(f"Failed processing event: {err}")
    finally:
        logging.info(f"Processed event in {time.time() - start:.{3}f}s")
