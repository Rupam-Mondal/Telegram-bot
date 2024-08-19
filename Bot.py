import configparser
import json
import asyncio
import re
import os
from datetime import datetime

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel
from const import api_id, api_hash  
from telelinks import *


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, bytes):
            return list(o)
        return json.JSONEncoder.default(self, o)


config = configparser.ConfigParser()
config.read("config.ini")

phone = config['Telegram']['phone']
username = config['Telegram']['username']


client = TelegramClient(username, api_id, api_hash)


output_directory = 'downloaded_images'
os.makedirs(output_directory, exist_ok=True)

async def scrape_messages_and_download_images(givenlink):
    link = givenlink
    await client.start()
    print("Client Created")

    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))

    me = await client.get_me()

    user_input_channel = link
    if user_input_channel.isdigit():
        entity = PeerChannel(int(user_input_channel))
    else:
        entity = user_input_channel

    my_channel = await client.get_entity(entity)

    offset_id = 0
    limit = 100
    all_messages = []
    total_messages = 0
    total_count_limit = 0

    image_count = 0  
    max_images = 20  

    while True:
        print("Current Offset ID is:", offset_id, "; Total Messages:", total_messages)
        history = await client(GetHistoryRequest(
            peer=my_channel,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))
        if not history.messages:
            break
        messages = history.messages
        for message in messages:
            all_messages.append(message.to_dict())
           
            if message.photo and image_count < max_images:
                photo = message.photo
                file_path = os.path.join(output_directory, f'{message.id}.jpg')
                await client.download_media(photo, file=file_path)
                image_count += 1
            
            if image_count >= max_images:
                break
        offset_id = messages[-1].id
        total_messages = len(all_messages)
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break
        if image_count >= max_images:
            break


    with open('channel_messages.json', 'w') as outfile:
        json.dump(all_messages, outfile, cls=DateTimeEncoder)


with client:
    client.loop.run_until_complete(scrape_messages_and_download_images(link4))


url_pattern = re.compile(r'https?://[^\s]+')


with open('channel_messages.json', 'r') as file:
    data = json.load(file)


with open('extracted_messages.txt', 'w', encoding='utf-8') as output_file:
    for message in data:
        if 'message' in message and not url_pattern.search(message['message']):
            output_file.write(message['message'] + '\n')

print("Messages without links have been successfully written to 'extracted_messages.txt'")


unique_links = set()
for message in data:
    if 'message' in message:
        urls = url_pattern.findall(message['message'])
        unique_links.update(urls)

with open('extracted_links.txt', 'w', encoding='utf-8') as output_file:
    for link in unique_links:
        output_file.write(link + '\n')

print(f"Extracted {len(unique_links)} unique links. They have been successfully written to 'extracted_links.txt'")
