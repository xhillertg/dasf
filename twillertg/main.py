import random
import time
import os
import itertools
import asyncio
from datetime import datetime
import colorama
from colorama import Fore, Style
from telethon import TelegramClient
from telethon.errors.rpcerrorlist import FloodWaitError, PhoneNumberInvalidError, UsernameInvalidError
from telethon.tl.types import InputMediaPhoto

# Set up your Telegram API credentials
api_id = 20918706
api_hash = 'a7de8dabdc9206f91400d6dca0968ed9'

# Function to log the message details
session_folder = os.path.join(os.getcwd(), "accounts")


def log_message(recipient, status):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f'{timestamp} - Recipient: {recipient}, Status: {status}'
    print(log_entry)


# Define a function to send a secret message
async def send_secret_message(session_name, recipient, message, image_path):
    session_path = os.path.join(session_folder, session_name)
    async with TelegramClient(session_path, api_id, api_hash) as client:
        try:
            if not await client.is_user_authorized():
                print("Error authorization")
                # Remove the session file from the folder
                os.remove(session_path)
                return False

            # Get the input entity of the recipient
            entity = await client.get_input_entity(recipient)

            # Check if user is currently online or recently online
            user = await client.get_entity(entity)
            if user.status:
                print(
                    f'User {recipient} has a status. Sending secret message...')
                try:
                    # Upload the image and get its file ID
                    image = await client.upload_file(image_path)
                    # Send the message with the image as a caption in the secret chat
                    await client.send_file(entity, file=image, caption=message)
                    print('Secret message sent!')
                    time.sleep(30)
                    log_message(recipient, 'Sent')
                    return True
                except FloodWaitError as e:
                    print(
                        f'Flood limit exceeded. Sleeping for {e.seconds} seconds...')
                    await asyncio.sleep(e.seconds)
                    log_message(recipient, 'Failed')
                    return False
                except Exception as e:
                    if "Too many requests" in str(e):
                        print(
                            f"{Fore.RED}Too many requests error occurred for {session_name}. Skipping...{Fore.RESET}")
                        # Mark the session as excluded
                        with open("excluded_sessions.txt", "a") as f:
                            f.write(f"{session_name}\n")
                    log_message(recipient, 'Failed')
                    return False
            else:
                print(f'User {recipient} is not currently online. Skipping...')
                log_message(recipient, 'Failed')
                return False
        except (PhoneNumberInvalidError, UsernameInvalidError):
            print("Invalid phone number or username. Skipping...")
            log_message(recipient, 'Failed')
            return False
        except Exception as e:
            if "Too many requests" in str(e):
                print(
                    f"{Fore.RED}Too many requests error occurred for {session_name}. Skipping...{Fore.RESET}")
                # Mark the session as excluded
                with open("excluded_sessions.txt", "a") as f:
                    f.write(f"{session_name}\n")
            log_message(recipient, 'Failed')
            return False


# Function to check if a session should be excluded
def should_exclude_session(session_name):
    excluded_sessions = []

    if os.path.exists("excluded_sessions.txt"):
        with open("excluded_sessions.txt", "r") as f:
            excluded_sessions = f.read().splitlines()

    return session_name in excluded_sessions


async def main():
    colorama.init()
    # Get a list of session names from the session folder
    session_names = [file for file in os.listdir(
        session_folder) if file.endswith('.session')]

    # Remove excluded sessions from the list of session names
    session_names = [
        session_name for session_name in session_names if not should_exclude_session(session_name)]

    session_cycle = itertools.cycle(session_names)
    current_session = next(session_cycle)  # Initialize with the first session

    # Read recipients from file
    with open('usernames.txt', 'r', encoding='utf-8') as f:
        recipients = [line.strip() for line in f.readlines()]

    # Get a list of message files in the messages directory
    message_files = [os.path.join("messages", f) for f in os.listdir(
        "messages") if os.path.isfile(os.path.join("messages", f))]

    success_count = 0
    failure_count = 0

    for recipient in recipients:
        # Select a random message file
        random_message_file = random.choice(message_files)

        # Read the message content from the file
        with open(random_message_file, 'r') as f:
            message_content = f.read().strip()

        # Select a random media file from the media folder
        media_folder = 'media'
        media_files = [os.path.join(media_folder, f) for f in os.listdir(
            media_folder) if os.path.isfile(os.path.join(media_folder, f))]
        random_media_file = random.choice(media_files)

        # Check if session file exists, if not, skip the recipient
        session_path = os.path.join(session_folder, current_session)
        if not os.path.isfile(session_path):
            print(
                f"Session file {current_session} not found. Skipping recipient {recipient}.")
            continue

        # Check if the current session has encountered too many requests
        if should_exclude_session(current_session):
            print(
                f"{Fore.RED}Current session {current_session} has encountered too many requests. Skipping recipient {recipient}.{Fore.RESET}")
            failure_count += 1
            current_session = next(session_cycle)
            continue

        # Send the secret message to the recipient using the current session
        result = await send_secret_message(current_session, recipient, message_content, random_media_file)
        if result:
            success_count += 1
        else:
            # Change session if an error occurs
            current_session = next(session_cycle)

    print(f"Total Success Count: {success_count}")
    print(f"Total Failure Count: {failure_count}")


# Example usage
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
