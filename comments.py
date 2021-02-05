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

def slack_comment(permalink, title, name, created_utc, created_utc_format, body_short, sentiment_outcome):
    print(f"Comment on: *<https://reddit.com{permalink}|{title}>* by <https://reddit.com/u/{name}|{name}>\n*Posted*: <!date^{round(created_utc)}^{{date_short_pretty}} {{time}}|{created_utc_format}>")
    client = WebClient(token=slack_token)
    message = json.load(open("msg_template.json", "r"))
    message[0]["text"]["text"] = f"Comment on: *<https://reddit.com{permalink}|{title}>* by <https://reddit.com/u/{name}|{name}>\n*Posted*: <!date^{round(created_utc)}^{{date_short_pretty}} {{time}}|{created_utc_format}>"
    message[2]["text"]["text"] = f"{body_short}..."
    message[3]["elements"]["text"] = f"{sentiment_outcome}"
    client.chat_postMessage(channel = slack_channel, blocks = message)
    return

def heartbeat(good_state, info):
    if good_state == true:
        requests.get(f"https://hc-ping.com/{config['healthcheck']['uuid']}", timeout=10)
    else:
        requests.post(f"https://hc-ping.com/{config['healthcheck']['uuid']}/fail", data=info)
    return

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
    global reddit, query, subreddit_name, slack_token, slack_channel
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
    return reddit, query, subreddit_name, slack_token, slack_channel

while True:
    try:
        load_config()
        analyzer = SentimentIntensityAnalyzer()
        for comment in reddit.subreddit(subreddit_name).stream.comments(pause_after=1, skip_existing=True):
            if comment is None:
                continue
            normalized_body = comment.body.lower()
            if query in normalized_body:
                comment.created_utc_format = datetime.fromtimestamp(comment.created_utc, tz=timezone.utc).isoformat()
                comment.body_short = comment.body[:280]
                print("Created: {}, Comment of: {}. Excerpt: {}... Upvotes: {}, Link: reddit.com{}".format(comment.created_utc_format, comment.submission.title, comment.body_short, comment.score, comment.permalink))
                compound_score = analyzer.polarity_scores(comment.body)["compound"]
                if compound_score > 0.5:
                    sentiment_outcome = ":slightly_smiling_face: Seems Positive"
                    slack_comment(permalink=comment.permalink, title=comment.submission.title, name=comment.author.name, created_utc=comment.created_utc, created_utc_format=comment.created_utc_format, body_short=comment.body_short, sentiment_outcome=sentiment_outcome)
                    heartbeat(good_state=True, info="Success")
                elif compound_score < 0:
                    sentiment_outcome = ":disappointed: Seems *Negative*"
                    slack_comment(permalink=comment.permalink, title=comment.submission.title, name=comment.author.name, created_utc=comment.created_utc, created_utc_format=comment.created_utc_format, body_short=comment.body_short, sentiment_outcome=sentiment_outcome)
                    heartbeat(good_state=True, info="Success")
                else:
                    sentiment_outcome = "¯\_(ツ)_/¯ Sorry I couldn't detect a substantial sentiment"
                    slack_comment(permalink=comment.permalink, title=comment.submission.title, name=comment.author.name, created_utc=comment.created_utc, created_utc_format=comment.created_utc_format, body_short=comment.body_short, sentiment_outcome=sentiment_outcome)
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