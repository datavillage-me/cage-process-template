import dv_tools

import logging

def processEvent(evt):
    """
    Process an incoming event
    """

    try:
        logging.info(f'Processing event {evt}')

        client = dv_tools.Client()

        # Use userIds provided in the event, or get all active users for this application
        user_ids = evt.get('userIds') if 'userIds' in evt else client.getUsers()

        for userId in user_ids:
            try:
                # retrieve data graph for user
                user_data = client.getData(userId)

                print(f'{len(user_data)} statements for user {userId}')

                client.writeResults(userId, "inferences", f'<https://datavillage.me/{userId}> <https://datavillage.me/count> {len(user_data)}')
            except Exception as err:
                logging.warning(f'Failed to process user {userId} : {err}')
    except Exception as err:
        logging.error(f'Failed processing event: {err}')


