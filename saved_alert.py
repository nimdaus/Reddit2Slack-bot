import praw
from praw.exceptions import RedditAPIException
from prawcore.exceptions import PrawcoreException
import json
from datetime import datetime, timezone
import requests
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from praw.models import Comment, Submission
#import os

def load_config():
    ## FOR WHEN DOCKERIZED
    #os.environ['client-id']
    #os.environ['client-secret']
    #os.environ['username']
    #os.environ['password']
    #os.environ['user-agent']
    #os.environ['query']
    #os.environ['subreddit']
    #os.environ['token']
    #os.environ['channel']
    global reddit, query, subreddit_name, slack_token, slack_channel, config
    config = json.load(open('config.json'))
    reddit = praw.Reddit(
        client_id=config['reddit']['client-id'],
        client_secret=config['reddit']['client-secret'],
        username=config['reddit']['username'],
        password=config['reddit']['password'],
        user_agent=config['reddit']['user_agent'])

    query = config['reddit']['query']
    subreddit_name = config['reddit']['subreddit']
    slack_token = config['slack']['token']
    slack_channel = config['slack']['channel']
    return reddit, query, subreddit_name, slack_token, slack_channel, config

def slack_submission(permalink, title, name, created_utc, created_utc_format):
    print(f"*<https://reddit.com{permalink}|{title}>* by <https://reddit.com/u/{name}|{name}>\n*Posted*: <!date^{round(created_utc)}^{{date_short_pretty}} {{time}}|{created_utc_format}>")
    client = WebClient(token=slack_token)
    message = json.load(open("save_alert.json", "r"))
    message[0]["text"]["text"] = f"<https://reddit.com{permalink}|{title}> by <https://reddit.com/u/{name}|{name}>\nPosted: <!date^{round(created_utc)}^{{date_short_pretty}} {{time}}|{created_utc_format}>"
    message[2]["text"]["text"] = f"*This post is being monitored by the Reddit Team :reddit: :eyes:*"
    client.chat_postMessage(channel = slack_channel, blocks = message)
    return

def heartbeat(good_state, info):
    if good_state == True:
        requests.get(f"https://hc-ping.com/{config['healthcheck']['uuid']}", timeout=10)
    else:
        requests.post(f"https://hc-ping.com/{config['healthcheck']['uuid']}/fail", data=info)
    return

while True:
    try:
        load_config()
        for item in reddit.user.me().saved.stream(pause_after=1, skip_existing=True):
            if isinstance(item, Comment):
                slack_submission(permalink=item.permalink, title=item.body[:140], name=item.author.name, created_utc=item.created_utc, created_utc_format=item.created_utc_format)
                heartbeat(good_state=True, info="Success")
            elif isinstance(item, Submission):
                slack_submission(permalink=item.permalink, title=item.title, name=item.author.name, created_utc=item.created_utc, created_utc_format=item.created_utc_format)
                heartbeat(good_state=True, info="Success")
    except RedditAPIException as e:
        print(f"ErrorMSG - {e}\nWaiting 5 seconds and trying again")
        heartbeat(good_state=False, info=f"{e}")
        time.sleep(5)
        continue
    except PrawcoreException as e:
        print(f"ErrorMSG - {e}\nWaiting 5 seconds and trying again")
        heartbeat(good_state=False, info=f"{e}")
        time.sleep(5)
        continue
    except SlackApiError as e:
        print(f"ErrorMSG - {e}\nWaiting 5 seconds and trying again")
        heartbeat(good_state=False, info=f"{e}")
        time.sleep(5)
        continue
    except Exception as e:
        print(f"ErrorMSG - {e}\nWaiting 5 seconds and trying again")
        heartbeat(good_state=False, info=f"{e}")
        time.sleep(5)
        quit()