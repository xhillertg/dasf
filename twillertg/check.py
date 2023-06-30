import asyncio
import os
from telethon import TelegramClient, errors

api_id = 20918706
api_hash = 'a7de8dabdc9206f91400d6dca0968ed9'

valid_accounts = 0


async def send_mes_to_users(client):
    global valid_accounts
    # Perform actions with the authorized client
    # Add your desired code here

    # Example: Print the name and number associated with the session
    me = await client.get_me()
    print(f"Name: {me.first_name} {me.last_name}")
    print(f"Number: {me.phone}")

    # Disconnect the client
    await client.disconnect()
    valid_accounts += 1


async def check_sessions():
    global valid_accounts
    # Specify the path to the "accounts" folder in Termux
    accounts_folder = "accounts"

    # Iterate over the session files in the accounts folder
    for file_name in os.listdir(accounts_folder):
        # Join the file name with the accounts folder path
        session_path = os.path.join(accounts_folder, file_name)

        # Skip any files that are not session files
        if not file_name.endswith(".session") or not os.path.isfile(session_path):
            continue

        # Extract the session name from the file name (remove the ".session" extension)
        session_name = os.path.splitext(file_name)[0]

        try:
            # Initialize the Telegram client with the session
            client = TelegramClient(
                session=session_path, api_id=api_id, api_hash=api_hash)

            # Connect the client
            await client.connect()

            # Check if the user is authorized
            if not await client.is_user_authorized():
                print(f"Error authorization for session: {session_name}")
                await client.disconnect()
                os.remove(session_path)
                print(f"Deleted session: {session_name}")
                continue

            # Perform actions with the authorized client
            await send_mes_to_users(client)
            print(f"Valid session: {session_name}")

        except errors.rpcerrorlist.PhoneNumberInvalidError:
            print(f"Invalid phone number for session: {session_name}")
            continue

# Create an event loop and run the check_sessions coroutine
loop = asyncio.get_event_loop()
loop.run_until_complete(check_sessions())

# Specify the path to excluded_sessions.txt in Termux
excluded_file_path = "excluded_sessions.txt"
if os.path.isfile(excluded_file_path):
    os.remove(excluded_file_path)
    print("Deleted excluded_sessions.txt")

print(f"Number of valid accounts: {valid_accounts}")
