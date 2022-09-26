import logging
from dv_utils import default_settings, Client
import time

logger = logging.getLogger(__name__)

# let the log go to stdout, as it will be captured by the cage operator
logging.basicConfig(
    level=default_settings.log_level,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# define an event processing function
def event_processor(evt: dict):
    """
    Process an incoming event
    """
    start = time.time()

    try:
        logger.info(f"Processing event {evt}")

        client = Client()

        # Use userIds provided in the event, or get all active users for this application
        user_ids = evt.get("userIds") if "userIds" in evt else client.get_users()

        logger.info(f"Processing {len(user_ids)} users")
        for user_id in user_ids:
            try:

                # retrieve data graph for user
                user_data = client.get_data(user_id)

                logger.info(f"{len(user_data)} statements for user {user_id}")

                # for the sake of this example, write some RDF with the number of user statements into the user's pod
                client.write_results(
                    user_id,
                    "inferences",
                    f"<https://datavillage.me/{user_id}> <https://datavillage.me/count> {len(user_data)}",
                )

            # pylint: disable=broad-except
            except Exception as err:
                logger.warning(f"Failed to process user {user_id} : {err}")

    # pylint: disable=broad-except
    except Exception as err:
        logger.error(f"Failed processing event: {err}")
    finally:
        logger.info(f"Processed event in {time.time() - start:.{3}f}s")