import dv_tools


def processEvent(evt):
    """
    Process an incoming event
    """

    client = dv_tools.Client()

    # Use userIds prvided in the event, or get all active users for this application
    user_ids = evt.get('userIds') if 'userIds' in evt else client.getUsers()

    for userId in user_ids:
        try:
            # retrieve data graph for user
            user_data = client.getData(userId)

            print(f'{len(user_data)} statements for user {userId}')
        except Exception as err:
            print(f'Failed to process user {userId} : {err}')


