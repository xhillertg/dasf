import re
import csv
from colorama import Fore, Style
from telethon import TelegramClient, events, utils

# Set up your Telegram API credentials
api_id = 25041499
api_hash = 'd67bc7f743de8e8816f6de798ccc7845'

# Create a new Telegram client instance
client = TelegramClient('scraper_acc', api_id, api_hash)


# Define an event handler to print the username of new messages in groups
@client.on(events.NewMessage)
async def new_message_handler(event):
    print(Fore.CYAN + f'{event.message.sender.username}' + Style.RESET_ALL)


async def main():
    # Start the client
    await client.start()

    # Get a list of all the dialogues (including both groups and private chats)
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            print(Fore.GREEN + f'{dialog.title}' + Style.RESET_ALL)

            # Get a list of all the users in the group
            participants = await client.get_participants(dialog)

            print(f"Found {len(participants)} users in {dialog.title}")

            with open('usernames.txt', 'a', encoding='utf-8') as f:
                for user in participants:
                    username = user.username
                    if username:
                        f.write(f'{username}\n')

            print(f"Members of {dialog.title} saved to usernames.txt")

    # Print "done" when finished
    print("done")

    # Prompt for an option to exit
    while True:
        option = input("Enter 'exit' to quit: ")
        if option.lower() == 'exit':
            break

    # Disconnect the client
    await client.disconnect()


if __name__ == '__main__':
    import asyncio

    # Create an event loop for Termux compatibility
    loop = asyncio.get_event_loop()

    # Run the main function
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
