import praw
from praw.exceptions import RedditAPIException
from prawcore.exceptions import PrawcoreException
from praw.models import Comment, Message
import json
from datetime import datetime, timezone
import requests
import time
from slack import WebClient

#Load config and declare specific variables
config = json.load(open('config.json'))

reddit = praw.Reddit(
    client_id=config['reddit']['client-id'],
    client_secret=config['reddit']['client-secret'],
    username=config['reddit']['username'],
    password=config['reddit']['password'],
    user_agent=config['reddit']['user_agent'])

slack_token = config['slack']['token-private']
slack_channel = config['slack']['channel-private']

while True:
    try:
        for item in reddit.inbox.stream(pause_after=1, skip_existing=True):
            if item is None:
                continue
            if isinstance(item, Message):
                item.created_utc_format = datetime.fromtimestamp(item.created_utc, tz=timezone.utc).isoformat()
                print(f"Created: {item.created_utc_format}, Author: {item.author}, Subject: {item.subject}, Excerpt: {item.body[:280]}")
                client = WebClient(token=slack_token)
                client.chat_postMessage(
                channel = slack_channel,
                blocks = [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Private Message* Subject: {item.subject}\nFrom:<https://reddit.com/u/{item.author}|{item.author}>*\n*Posted*: <!date^{round(item.created_utc)}^{{date_short_pretty}} {{time}}|{item.created_utc_format}>"
                        }
                        },
                        {
                            "type": "divider"
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"{item.body[:280]}..."
                            }
                        },
                    ]
                )
            elif isinstance(item, Comment):
                item.created_utc_format = datetime.fromtimestamp(item.created_utc, tz=timezone.utc).isoformat()
                print(f"Created: {item.created_utc_format}, Author: {item.author}, Excerpt: {item.body[:280]}")
                client = WebClient(token=slack_token)
                client.chat_postMessage(
                channel = slack_channel,
                blocks = [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Private Message* Subject: {item.subject}\nFrom:<https://reddit.com/u/{item.author}|{item.author}>*\n*Posted*: <!date^{round(item.created_utc)}^{{date_short_pretty}} {{time}}|{item.created_utc_format}>"
                        }
                        },
                        {
                            "type": "divider"
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"{item.body[:280]}..."
                            }
                        },
                    ]
                )
    except RedditAPIException as exception:
        print("error - waiting 5 seconds and trying again")
        time.sleep(5)
        continue
    except PrawcoreException as e:
        print("error - waiting 5 seconds and trying again")
        time.sleep(5)
        continue