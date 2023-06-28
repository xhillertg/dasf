import os
import pickle
from telethon.sync import TelegramClient


def add_number():
    while True:
        phone_number = input(
            "Enter your phone number (in international format), or enter 'exit' to quit: ")

        if phone_number.lower() == 'exit':
            print("Exiting...")
            return

        session_dir = "accounts"
        # Create session directory if it does not exist
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)

        session_file = os.path.join(session_dir, f'session_{phone_number}')
        api_id = 20918706
        api_hash = 'a7de8dabdc9206f91400d6dca0968ed9'
        client1 = TelegramClient(session_file, api_id, api_hash)
        try:
            client1.start()
        except Exception as e:
            print(f"Error starting client for session {session_file}: {e}")
            return
        client1.disconnect()
        print(f"Session file for {phone_number} created: {session_file}")

        # Load the existing session dictionary
        if os.path.exists("session_dict1.pickle"):
            with open("session_dict1.pickle", "rb") as f:
                session_dict = pickle.load(f)
        else:
            session_dict = {}

        # Update the session dictionary
        session_dict[phone_number] = session_file

        # Save the updated session dictionary
        with open("session_dict1.pickle", "wb") as f:
            pickle.dump(session_dict, f)

        choice = input(
            "Session added successfully. Do you want to add another number? (yes/no): ")
        if choice.lower() != 'yes':
            print("Exiting...")
            return


if __name__ == '__main__':
    add_number()
