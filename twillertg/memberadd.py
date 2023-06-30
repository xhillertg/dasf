import os
import time
from colorama import Fore, Style
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest, InviteToChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.errors import FloodWaitError, InviteHashExpiredError, UserPrivacyRestrictedError, ChatWriteForbiddenError
from datetime import datetime, timedelta
from telethon.tl.types import UserStatusOnline, UserStatusRecently, UserStatusOffline
import pytz

# Set up your Telegram API credentials
api_id = 29393268
api_hash = '4cb45217fc8a9ef2df4a4c6487d25cd2'

# Function to join a channel using a specific session


def join_channel_with_session(session_name, channel_username, is_private, invite_link=None):
    session_path = os.path.join("accounts", session_name)
    with TelegramClient(session_path, api_id, api_hash) as client:
        try:
            if is_private and invite_link:
                client(ImportChatInviteRequest(invite_link))
            else:
                client(JoinChannelRequest(channel_username))
            print(f"Session {session_name} joined the channel")
            time.sleep(5)  # Add a delay of 5 seconds after joining the channel
        except FloodWaitError as e:
            print(f"{Fore.RED}Failed to join the channel using session {session_name}: Flood wait for {e.seconds} seconds{Style.RESET_ALL}")
            return  # Skip the session
        except Exception as e:
            print(
                f"{Fore.RED}Failed to join the channel using session {session_name}: {str(e)}{Style.RESET_ALL}")
            return  # Skip the session

        add_members_to_channel(client, channel_username)

        # Disconnect the client after processing the session
        client.disconnect()


def remove_member_from_file(member):
    with open("usernames.txt", "r") as f:
        recipients = f.readlines()

    if member + '\n' in recipients:
        recipients.remove(member + '\n')

    with open("usernames.txt", "w") as f:
        f.writelines(recipients)


def add_members_to_channel(client, channel_username):
    # Read the members from a file or any other source
    with open("usernames.txt", "r") as f:
        members = [line.strip() for line in f.readlines()]

    added_members = []  # List to store successfully added members
    skipped_members = []  # List to store skipped members

    # Retrieve all participants in the channel
    participants = client.get_participants(channel_username)
    # Set of participant usernames
    participant_usernames = {
        participant.username for participant in participants}

    desired_timezone = pytz.timezone('Asia/Manila')
    now = datetime.now(desired_timezone)

    for member in members:
        try:
            print(f"{Fore.CYAN}Processing member: {member}{Style.RESET_ALL}")
            user = client.get_entity(member)
            if user.username in participant_usernames:
                print(
                    f"{Fore.YELLOW}Skipping {member} as the user is already in the channel{Style.RESET_ALL}")
                remove_member_from_file(member)
                time.sleep(10)
                added_members.append(member)
            else:
                user_status = user.status
                if isinstance(user_status, (UserStatusOnline, UserStatusRecently)) or (hasattr(user_status, 'was_online') and user_status.was_online + timedelta(hours=5) >= now):
                    print(
                        f"{Fore.GREEN}User status: {user_status.__class__.__name__}{Style.RESET_ALL}")
                    if isinstance(user_status, UserStatusRecently):
                        print(f"{Fore.YELLOW}Last online: N/A{Style.RESET_ALL}")
                        client(InviteToChannelRequest(
                            channel_username, [user]))
                        added_members.append(member)
                        print(
                            f"{Fore.GREEN}Added {member} to the channel{Style.RESET_ALL}")
                        remove_member_from_file(member)
                        time.sleep(10)
                    elif isinstance(user_status, UserStatusOnline):
                        print(f"{Fore.YELLOW}Last online: N/A{Style.RESET_ALL}")
                        client(InviteToChannelRequest(
                            channel_username, [user]))
                        added_members.append(member)
                        print(
                            f"{Fore.GREEN}Added {member} to the channel{Style.RESET_ALL}")
                        remove_member_from_file(member)
                        time.sleep(10)
                    else:
                        last_online = user_status.was_online.astimezone(
                            desired_timezone)
                        last_online_str = last_online.strftime(
                            "%Y-%m-%d %H:%M:%S")
                        print(
                            f"{Fore.YELLOW}Last online: {last_online_str}{Style.RESET_ALL}")
                        print(
                            f"{Fore.GREEN}User status: {user_status.__class__.__name__}{Style.RESET_ALL}")
                        client(InviteToChannelRequest(
                            channel_username, [user]))
                        added_members.append(member)
                        print(
                            f"{Fore.GREEN}Added {member} to the channel{Style.RESET_ALL}")
                        remove_member_from_file(member)
                        time.sleep(10)
                else:
                    if hasattr(user_status, 'was_online'):
                        last_online = user_status.was_online.astimezone(
                            desired_timezone)
                        last_online_str = last_online.strftime(
                            "%Y-%m-%d %H:%M:%S")
                        print(
                            f"{Fore.YELLOW}Last online: {last_online_str}{Style.RESET_ALL}")
                    print(
                        f"{Fore.YELLOW}Skipping {member} as the user was not online within the last 5 hours{Style.RESET_ALL}")
                    remove_member_from_file(member)
                    time.sleep(10)

            time.sleep(2)

        except FloodWaitError as e:
            print(
                f"{Fore.RED}Skipping {member} due to flood wait for {e.seconds} seconds{Style.RESET_ALL}")
            time.sleep(10)
            return
        except InviteHashExpiredError:
            print(
                f"{Fore.RED}Skipping {member} due to expired invite link{Style.RESET_ALL}")
            remove_member_from_file(member)
            time.sleep(10)
            break
        except UserPrivacyRestrictedError:
            print(
                f"{Fore.RED}Skipping {member} due to user privacy restrictions{Style.RESET_ALL}")
            remove_member_from_file(member)
            time.sleep(10)
        except ChatWriteForbiddenError as e:
            if "You're banned from sending messages in supergroups/channels" in str(e):
                print(
                    f"{Fore.RED}Skipping {member} due to being banned from sending messages in supergroups/channels{Style.RESET_ALL}")
                time.sleep(10)
                return
            skipped_members.append(member)
        except Exception as e:
            if "You're banned from sending messages in supergroups/channels" in str(e):
                print(
                    f"{Fore.RED}You're banned error occurred. Skipping...{Style.RESET_ALL}")
                time.sleep(10)
                return
            elif "Too many requests" in str(e):
                print(
                    f"{Fore.RED}Too many requests error occurred. Change session.{Style.RESET_ALL}")
                return
            else:
                print(
                    f"{Fore.RED}Failed to add {member} to the channel: {str(e)}{Style.RESET_ALL}")
                remove_member_from_file(member)
                time.sleep(10)

    # Update the file with the remaining members
    with open("usernames.txt", "w") as f:
        f.write("\n".join(members))

    # Append the added and skipped members to their respective lists
    added_members.extend(added_members)
    skipped_members.extend(skipped_members)


def main():
    # Read the channel username from input
    channel_username = input("Enter the channel username (without @): ")

    # Prompt whether the group is private or public
    is_private = input("Is the group private? (Y/N): ").lower() == 'y'

    # Read session names from the "accounts" folder
    session_names = [file for file in os.listdir(
        "accounts") if file.endswith('.session')]

    # Join the channel using each session
    for session_name in session_names:
        print(f"{Fore.CYAN}Processing session: {session_name}{Style.RESET_ALL}")
        join_channel_with_session(session_name, channel_username, is_private)
        time.sleep(10)  # Add a delay of 10 seconds between joining attempts


# Run the main function
if __name__ == "__main__":
    main()
