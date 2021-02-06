import praw
from praw.exceptions import RedditAPIException
from prawcore.exceptions import PrawcoreException
import json
from datetime import datetime, timezone
import requests
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
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

def slack_submission(permalink, title, name, created_utc, created_utc_format, self_text, sentiment):
    print(f"*<https://reddit.com{permalink}|{title}>* by <https://reddit.com/u/{name}|{name}>\n*Posted*: <!date^{round(created_utc)}^{{date_short_pretty}} {{time}}|{created_utc_format}>")
    client = WebClient(token=slack_token)
    message = json.load(open("msg_template.json", "r"))
    message[0]["text"]["text"] = f"*<https://reddit.com{permalink}|{title}>* by <https://reddit.com/u/{name}|{name}>\n*Posted*: <!date^{round(created_utc)}^{{date_short_pretty}} {{time}}|{created_utc_format}>"
    message[2]["text"]["text"] = f"{self_text}"
    message[3]["elements"]["text"] = f"{sentiment}"
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
        analyzer = SentimentIntensityAnalyzer()
        for submission in reddit.subreddit(subreddit_name).stream.submissions(pause_after=1, skip_existing=True):
            if submission is None:
                continue
            normalized_title = submission.title.lower()
            if query in normalized_title:
                submission.created_utc_format = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc).isoformat()
                print("Created: {}, Title: {}".format(submission.created_utc_format, submission.title))
                compound_score = analyzer.polarity_scores(submission.selftext)["compound"]
                if compound_score > 0.5:
                    sentiment = ":slightly_smiling_face: Seems *Positive*"
                    slack_submission(permalink=submission.permalink, title=submission.title, name=submission.author.name, created_utc=submission.created_utc, created_utc_format=submission.created_utc_format, self_text=submission.selftext, sentiment=sentiment)
                    heartbeat(good_state=True, info="Success")
                elif compound_score < 0:
                    sentiment = ":dissappointed: Seems *Negative*"
                    slack_submission(permalink=submission.permalink, title=submission.title, name=submission.author.name, created_utc=submission.created_utc, created_utc_format=submission.created_utc_format, self_text=submission.selftext, sentiment=sentiment)
                    heartbeat(good_state=True, info="Success")
                else:
                    sentiment = "¯\_(ツ)_/¯ Sorry I couldn't detect a substantial sentiment"
                    slack_submission(permalink=submission.permalink, title=submission.title, name=submission.author.name, created_utc=submission.created_utc, created_utc_format=submission.created_utc_format, self_text=submission.selftext, sentiment=sentiment)
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