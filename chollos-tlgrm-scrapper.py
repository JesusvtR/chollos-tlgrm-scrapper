import time
import requests
import json
import traceback
import logging
from datetime import datetime
from discord_webhook import DiscordWebhook, DiscordEmbed
from bs4 import *

logging.basicConfig(filename='info.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')

full_message = {}
headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"}

def send_chollo(webhook, full_message):
    embed = DiscordEmbed(title='Chollo', url=full_message['link'], description=full_message['text'])
    embed.set_image(url=full_message["url_image"])
    embed.set_footer(text=f"New: "+ full_message["timestamp"])
    webhook.add_embed(embed)
    logging.info(embed.description)
    response = webhook.execute(True)

def readFile(path):
    file = open(path, "r")
    content = file.read()
    file.close()
    content = content.split(",")
    return content

def readJson(path):
    try:
        with open(path, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
    return data

def main():
    print("Starting...")
    config_data = readJson("config.json")
    # Check if the "webhook" field is already filled
    if "webhook" in config_data and config_data["webhook"]:
        pass
    else:
        # Ask the user to enter the webhook link
        webhook_link = input("Enter the webhook link: ")

        # Update the "webhook" field in the dictionary
        config_data["webhook"] = webhook_link

        # Save the data in the JSON file
        with open("config.json", "w") as file:
            json.dump(config_data, file)

        print("The webhook link has been successfully configured.")

    webhook = DiscordWebhook(url=config_data["webhook"])
    # Check if the "delay" field is already filled
    if "delay" in config_data and config_data["delay"]:
        pass
    else:
        # Ask the user to enter the delay
        delay = input("Enter the delay: ")

        # Update the "webhook" field in the dictionary
        config_data["delay"] = delay

        # Save the data in the JSON file
        with open("config.json", "w") as file:
            json.dump(config_data, file)

        print("The delay has been successfully configured.")

    delay = int(config_data["delay"])

    # Check if the "urls" field is already filled
    if "urls" in config_data and config_data["urls"]:
        pass
    else:
        # Ask the user to enter the telegram links
        urls = input("Enter the telegram links: ")

        # Update the "webhook" field in the dictionary
        config_data["urls"] = urls

        # Save the data in the JSON file
        with open("config.json", "w") as file:
            json.dump(config_data, file)

        print("The urls have been successfully configured.")

    urls = config_data["urls"]

    while True:
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            keywords = readFile("keywords.txt")
            irrwords = readFile("irrwords.txt")
            for channels_url in urls:
                channel = requests.get(channels_url).text
                soup = BeautifulSoup(channel, 'lxml')
                tgpost = soup.find_all('div', class_ ='tgme_widget_message')
                for content in tgpost:
                    full_message['timestamp'] = content.find('time', class_ = 'time').text
                    if content.find('div', class_ = 'tgme_widget_message_text') is not None:
                        full_message['text'] = content.find('div', class_ = 'tgme_widget_message_text').text
                    full_message['link'] =  content.a['href']
                    if content.find('a', class_ = 'tgme_widget_message_link_preview') != None :
                        link = content.find('a', class_ = 'tgme_widget_message_link_preview')
                        full_message['url_image'] = link.get('href')
                    else:
                        full_message['url_image'] = 'https://cdn.personalitylist.com/avatars/119290.png'
                    for keyword in keywords:
                        if keyword in full_message['text']:
                            if all(irrword not in full_message['text'] for irrword in irrwords):
                                send_chollo(webhook, full_message)
                            else:
                                continue
            print(f"[{timestamp}]"+" Running...")
            logging.info(f"[{timestamp}]"+" Running...")        
            time.sleep(delay)
            pass
        except Exception as exception:
            print(f"[{timestamp}]{exception}")
            error = traceback.format_exc()
            logging.warning(error)
            time.sleep(delay)

if __name__ == '__main__':
    main()
