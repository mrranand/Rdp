import asyncio
import os
import json
import random
import logging
from telethon import TelegramClient, events, errors
from telethon.errors import SessionPasswordNeededError, UserDeactivatedBanError
from telethon.tl.functions.messages import GetHistoryRequest
from colorama import init, Fore
import pyfiglet

# Initialize colorama for colored output
init(autoreset=True)

# Define session folder
CREDENTIALS_FOLDER = 'sessions'
os.makedirs(CREDENTIALS_FOLDER, exist_ok=True)

# Set up logging
logging.basicConfig(
    filename='og_flame_service.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Updated Auto-Reply Message
AUTO_REPLY_MESSAGE = """
💯𝗛𝗲𝘆 𝘀𝗶𝗿. 

𝗣𝗹𝗲𝗮𝘀𝗲 𝗺𝗲𝘀𝘀𝗮𝗴𝗲 @Eclipvan  👑 👈🏻 . 𝗶𝗳 𝘆𝗼𝘂'𝗿𝗲 𝗶𝗻𝘁𝗲𝗿𝗲𝘀𝘁𝗲𝗱 𝗶𝗻 𝗯𝘂𝘆𝗶𝗻𝗴 𝗼𝘂𝗿 𝘀𝗲𝗿𝘃𝗶𝗰𝗲. 

➡️ 𝗧𝗵𝗶𝘀 𝗶𝘀 𝗷𝘂𝘀𝘁 𝗮 𝗽𝗿𝗼𝗺𝗼𝘁𝗶𝗼𝗻𝗮𝗹 𝘄𝗼𝗿𝗸𝗶𝗻𝗴 𝗜𝗗. 𝗧𝗵𝗮𝗻𝗸𝘀 𝗳𝗼𝗿 𝘃𝗶𝘀𝗶𝘁𝗶𝗻𝗴 𝘂𝘀! 🙏  

💼 𝗢𝘂𝗿 𝗰𝗵𝗮𝗻𝗻𝗲𝗹: @Eclipvan    ✅️   👈🏻
🕷 𝗢𝘂𝗿 𝗽𝗿𝗼𝗼𝗳𝘀:   @Eclipvan    ✅️.   👈🏻
"""

def display_banner():
    """Display the banner using pyfiglet."""
    print(Fore.RED + pyfiglet.figlet_format("iAbuse"))
    print(Fore.GREEN + "Made by @iAbused\n")

# Function to save session credentials
def save_credentials(session_name, credentials):
    path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")
    with open(path, "w") as f:
        json.dump(credentials, f)

# Function to load session credentials
def load_credentials(session_name):
    path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

async def get_last_saved_message(client):
    """Retrieve the last message from 'Saved Messages'."""
    try:
        saved_messages_peer = await client.get_input_entity('me')
        history = await client(GetHistoryRequest(
            peer=saved_messages_peer,
            limit=1,
            offset_id=0,
            offset_date=None,
            add_offset=0,
            max_id=0,
            min_id=0,
            hash=0
        ))
        return history.messages[0] if history.messages else None
    except Exception as e:
        logging.error(f"Failed to retrieve saved messages: {str(e)}")
        return None

async def forward_messages_to_groups(client, last_message, session_name, rounds, delay_between_rounds):
    """Forward the last saved message to all groups."""
    try:
        group_dialogs = [dialog for dialog in await client.get_dialogs() if dialog.is_group]
        print(Fore.CYAN + f"Found {len(group_dialogs)} groups for session {session_name}")

        if not group_dialogs:
            logging.warning(f"No groups found for session {session_name}.")
            return

        for round_num in range(1, rounds + 1):
            print(Fore.YELLOW + f"\nStarting round {round_num} for session {session_name}...")
            forward_count = 0  # Counter for forwarded messages

            for dialog in group_dialogs:
                group = dialog.entity
                try:
                    await client.forward_messages(group, last_message)
                    forward_count += 1  # Increment the counter
                    print(Fore.GREEN + f"Message forwarded to {group.title} using {session_name}")
                    logging.info(f"Message forwarded to {group.title} using {session_name}")

                    # Clear the screen after every 50 forwards
                    if forward_count % 50 == 0:
                        os.system('clear' if os.name == 'posix' else 'cls')
                        print(Fore.MAGENTA + f"Screen cleared after {forward_count} forwards.")

                except errors.FloodWaitError as e:
                    print(Fore.RED + f"Rate limit exceeded. Waiting for {e.seconds} seconds.")
                    await asyncio.sleep(e.seconds)
                    await client.forward_messages(group, last_message)
                    print(Fore.GREEN + f"Message forwarded to {group.title} after waiting.")
                except Exception as e:
                    print(Fore.RED + f"Failed to forward message to {group.title}: {str(e)}")
                    logging.error(f"Failed to forward message to {group.title}: {str(e)}")

                delay = random.randint(5, 10)  # Updated delay to 5-10 seconds
                print(f"Waiting for {delay} seconds before forwarding to the next group...")
                await asyncio.sleep(delay)

            print(Fore.GREEN + f"Round {round_num} completed for session {session_name}.")
            if round_num < rounds:
                print(Fore.CYAN + f"Waiting for {delay_between_rounds} seconds before next round...")
                await asyncio.sleep(delay_between_rounds)

    except Exception as e:
        logging.error(f"Unexpected error in forward_messages_to_groups: {str(e)}")

async def auto_reply(client, session_name):
    """Auto-reply to private messages."""
    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        if event.is_private:
            try:
                await event.reply(AUTO_REPLY_MESSAGE)
                logging.info(f"Replied to {event.sender_id} in session {session_name}")
            except errors.FloodWaitError as e:
                await asyncio.sleep(e.seconds)
            except Exception as e:
                logging.error(f"Failed to reply to {event.sender_id}: {str(e)}")

async def main():
    """Main function to handle user input and execute the script."""
    display_banner()

    try:
        num_sessions = int(input("Enter the number of sessions: "))
        if num_sessions <= 0:
            print(Fore.RED + "Number of sessions must be greater than 0.")
            return

        clients = []
        valid_clients = []

        for i in range(1, num_sessions + 1):
            session_name = f"session{i}"
            credentials = load_credentials(session_name)

            if credentials:
                api_id = credentials["api_id"]
                api_hash = credentials["api_hash"]
                phone_number = credentials["phone_number"]
            else:
                api_id = int(input(Fore.CYAN + f"Enter API ID for session {i}: "))
                api_hash = input(Fore.CYAN + f"Enter API hash for session {i}: ")
                phone_number = input(Fore.CYAN + f"Enter phone number for session {i}: ")

                credentials = {
                    "api_id": api_id,
                    "api_hash": api_hash,
                    "phone_number": phone_number,
                }
                save_credentials(session_name, credentials)

            client = TelegramClient(session_name, api_id, api_hash)

            try:
                await client.start(phone=phone_number)
                print(Fore.GREEN + f"Logged in successfully for session {i}")
                valid_clients.append(client)
            except UserDeactivatedBanError:
                print(Fore.RED + f"Session {i} is banned. Skipping...")
                logging.warning(f"Session {i} is banned. Skipping...")
                continue
            except Exception as e:
                print(Fore.RED + f"Failed to login for session {i}: {str(e)}")
                logging.error(f"Failed to login for session {i}: {str(e)}")
                continue

        if not valid_clients:
            print(Fore.RED + "No valid accounts available to proceed.")
            return

        print(Fore.MAGENTA + "\nChoose an option:")
        print(Fore.YELLOW + "1. Auto Forwarding (Forward last saved message to all groups)")
        print(Fore.YELLOW + "2. Auto Reply (Reply to private messages)")

        option = int(input(Fore.CYAN + "Enter your choice: "))
        rounds, delay_between_rounds = 0, 0

        if option == 1:
            rounds = int(input(Fore.MAGENTA + "How many rounds should the message be sent? "))
            delay_between_rounds = int(input(Fore.MAGENTA + "Enter delay (in seconds) between rounds: "))
            print(Fore.GREEN + "Starting Auto Forwarding...")

            tasks = []
            for client in valid_clients:
                last_message = await get_last_saved_message(client)
                if last_message:
                    tasks.append(forward_messages_to_groups(client, last_message, client.session.filename, rounds, delay_between_rounds))
                    tasks.append(auto_reply(client, client.session.filename))

            await asyncio.gather(*tasks)
        elif option == 2:
            print(Fore.GREEN + "Starting Auto Reply...")
            tasks = [auto_reply(client, client.session.filename) for client in valid_clients]
            await asyncio.gather(*tasks)

        for client in valid_clients:
            await client.disconnect()

    except KeyboardInterrupt:
        print(Fore.YELLOW + "\nScript terminated by user.")

if __name__ == "__main__":
    asyncio.run(main())